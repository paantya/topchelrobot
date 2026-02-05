import os
import re
import json
import calendar
import time, datetime

from pathlib import Path

from const import DISABLE_NOTIFICATION, TIME_SHIFT

def file_exist_and_touch(file):
    path = Path(file)

    if not path.is_file():
        print(f'The file `{path.resolve()}` does not exist ({path.parent})', end=' ')
        path.parent.resolve().mkdir(parents=True, exist_ok=True)
        path.resolve().touch()
        print(f'touch file `{path.resolve()}`', end=' ')
        with open(path, 'w') as f:
            json.dump({}, f, ensure_ascii=False, indent=1)
        print(f'Create empty json.')
    else:
        # print(f'The file `{path.resolve()}` exists')
        pass


def load(file):
    file_exist_and_touch(file)
    with open(file, 'r') as f:
        data = json.load(f)
    return data


def save(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def get_name(users_json=None, id=None, user=None):
    if user is None:
        if id in users_json['join']:
            user_json = users_json['join'][id]
        if id in users_json['detach']:
            user_json = users_json['detach'][id]
    else:
        user_json = user
    name = ''
    if 'first_name' in user_json and len(user_json['first_name']) > 0:
        name += f"*{user_json['first_name']}*"
    if 'last_name' in user_json and len(user_json['last_name']) > 0:
        if len(name) > 0:
            name += ' '
        name += f"*{user_json['last_name']}*"
    if 'username' in user_json and len(user_json['username']) > 0:
        if len(name) > 0:
            name += f" (`{user_json['username']}`)"
        else:
            name += f"*{user_json['username']}*"
    return name


def get_top_list(bot, message, period_months=1, all=False, top_n=10, all_time=False):

    activity_time_all = 0
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)

    get_time = time.time()
    get_time_dt = datetime.datetime.fromtimestamp(get_time)

    file_historys = []
    since_text = ''
    if all_time:
        files = []
        for filename in os.listdir(f"./data/{type}{message_json['chat']['id']}/"):
            if filename != 'info.json':
                files.append(filename)
        since = sorted(files)[0].replace('.json','')
        since_dt = datetime.datetime.strptime(since, '%Y-%m')
        since_dt_text = since_dt.strftime("%B %Y")
        since_text = f' since {since_dt_text}'
        for filename in files:
            file_history = f"./data/{type}{message_json['chat']['id']}/{filename}"
            file_historys.append(file_history)

            match = re.search(r'(\d{4})-(\d{2})\.json', filename)
            if match:
                year = int(match.group(1))  # Группа 1 - это год
                month = int(match.group(2))  # Группа 2 - это месяц
                _, num_days = calendar.monthrange(year, month)
                activity_time_all += num_days

        # print(file_historys)
    else:
        for i in range(period_months):
            year = get_time_dt.year + (get_time_dt.month - i - 1) // 12
            month = (get_time_dt.month - i - 1) % 12 + 1

            file_name = datetime.datetime.strptime(f'{year}-{month}', '%Y-%m').strftime("%Y-%m")
            file_history = f"./data/{type}{message_json['chat']['id']}/{file_name}.json"
            if os.path.exists(file_history):
                file_historys.append(file_history)

                _, num_days = calendar.monthrange(year, month)
                activity_time_all += num_days

    history = {}

    current_date = datetime.datetime.now()
    _, num_days = calendar.monthrange(current_date.year, current_date.month)
    all_days_in_time_now = activity_time_all + current_date.day - num_days


    sum_top = 0
    for file_history in file_historys:
        info_history = load(file=file_history)
        if 'top' not in info_history.keys():
            info_history['top'] = {}
        for k,v in info_history['top'].items():
            if k not in history.keys():
                history[k] = 0
            history[k] += v
            sum_top += v
    lost_days = all_days_in_time_now - sum_top

    if len(history) < 1:
        text =  f"За выбранный период нет статистики."
        bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                         disable_notification=DISABLE_NOTIFICATION)
        return None
    text = ''
    sorted_tuples = sorted(history.items(), key=lambda item: item[1], reverse=True)
    # Топ - 10 пидоров за текущий год:
    #
    # Всего участников — 18
    top_score = 0
    i_sum = 0
    for i, (id, n) in enumerate(sorted_tuples):
        user = {"first_name": "no_name"}
        if id in info['detach']:
            user = info['detach'][id]
        if id in info['join']:
            user = info['join'][id]
        name = get_name(user=user)
        if all or (i < top_n or top_score == n):
            top_score = n
            text += f"`{(i + 1): >2}.` {n} -- {name}\n"
            i_sum += 1
        else:
            break
    total = len(sorted_tuples)
    text_lost_day = f'\nПропущено разыгрышей за период активных месяцев -- {lost_days}' if all and lost_days > 0 else ''
    text_win_rate = f'\nРеализовано {sum_top} из {activity_time_all} побед до конца месяца' if all else ''
    text_top = f'top {i_sum}' if not all else 'all'
    text = f"Рейтинг ({text_top}{since_text}):\n\n{text}\nВсего победителей -- {total}{text_win_rate}{text_lost_day}"
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)

    return text


def get_top_statistics(bot, message, period_months=1, all_time=False):
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)

    get_time = time.time()
    get_time_dt_ = datetime.datetime.fromtimestamp(get_time)
    year = get_time_dt_.year + (get_time_dt_.month - 1 - 1) // 12
    month = (get_time_dt_.month - 1 - 1) % 12 + 1
    get_time_dt = get_time_dt_.replace(year=year, month=month)

    files = []
    file_now = f"{get_time_dt_.year:0>4}-{get_time_dt_.month:0>2}.json"
    if all_time:
        for filename in os.listdir(f"./data/{type}{message_json['chat']['id']}/"):
            if filename != 'info.json' and filename != file_now:
                files.append(filename)
    else:
        for i in range(period_months):
            year = get_time_dt.year + (get_time_dt.month - i - 1) // 12
            month = (get_time_dt.month - i - 1) % 12 + 1
            file_name = datetime.datetime.strptime(f'{year}-{month}', '%Y-%m').strftime("%Y-%m")
            file_history = f"./data/{type}{message_json['chat']['id']}/{file_name}.json"
            if os.path.exists(file_history):
                files.append(f"{file_name}.json")
    text = ""
    for filename in sorted(files, reverse=True):
        file_history = f"./data/{type}{message_json['chat']['id']}/{filename}"
        info_history = load(file=file_history)

        date_loc = datetime.datetime.strptime(filename.replace('.json',''), '%Y-%m')
        date_loc_text = date_loc.strftime("%Y %b")

        _, num_days = calendar.monthrange(date_loc.year, date_loc.month)

        sum_top = 0
        for k,v in info_history['top'].items():
            sum_top += v

        text += f"*{date_loc_text}* (win rate: {sum_top}/{num_days} ~ {int(sum_top/num_days*100)}%):\n"


        for i, win in enumerate(info_history['win']):
            name = get_name(info, str(win['id']))
            text += f"-- `{win['n']}` {name}\n"
        text += f"\n"

    if len(files) < 1:
        text = f"За выбранный период нет статистики."
        bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                         disable_notification=DISABLE_NOTIFICATION)
        return None

    text = f"Отличились за последние месяцы:\n{text}"
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)
    return text


def get_earliest_history_dt(chat_type, chat_id):
    data_dir = f"./data/{chat_type}{chat_id}/"
    if not os.path.isdir(data_dir):
        return None

    earliest = None
    for filename in os.listdir(data_dir):
        match = re.search(r'(\d{4})-(\d{2})\.json', filename)
        if not match:
            continue
        year = int(match.group(1))
        month = int(match.group(2))
        if earliest is None or (year, month) < earliest:
            earliest = (year, month)

    if earliest is None:
        return None
    return datetime.datetime(year=earliest[0], month=earliest[1], day=1)


def build_previous_month_summary(info, chat_type, chat_id, current_dt, last_run_dt=None, include_all=False):
    def format_name(user_id):
        user = {"first_name": "no_name"}
        if user_id in info.get('detach', {}):
            user = info['detach'][user_id]
        if user_id in info.get('join', {}):
            user = info['join'][user_id]
        return get_name(user=user)

    summaries = []
    if include_all:
        if last_run_dt is None:
            return None
        start_year = last_run_dt.year
        start_month = last_run_dt.month
        end_year = current_dt.year
        end_month = current_dt.month

        total_months = (end_year - start_year) * 12 + (end_month - start_month)
        offsets = range(total_months)
    else:
        year = current_dt.year
        month = current_dt.month - 1
        if month == 0:
            month = 12
            year -= 1
        if year < 1:
            return None
        start_year = year
        start_month = month
        offsets = range(1)

    for offset in offsets:
        year = start_year + (start_month - 1 + offset) // 12
        month = (start_month - 1 + offset) % 12 + 1
        file_name = datetime.datetime.strptime(f'{year}-{month}', '%Y-%m').strftime("%Y-%m")
        file_history = f"./data/{chat_type}{chat_id}/{file_name}.json"
        if not os.path.exists(file_history):
            continue

        info_history = load(file=file_history)
        if 'top' not in info_history or len(info_history['top']) < 1:
            continue

        sorted_tuples = sorted(info_history['top'].items(), key=lambda item: item[1], reverse=True)
        top_score = sorted_tuples[0][1]
        winners = [item for item in sorted_tuples if item[1] == top_score]

        rankings = []
        place = 0
        previous_score = None
        for user_id, score in sorted_tuples:
            if score != previous_score:
                place += 1
                previous_score = score
            rankings.append((place, user_id, score))

        top_entries = [entry for entry in rankings if entry[0] <= 3]

        month_title = f"{year:0>4}-{month:0>2}"
        winner_label = "победителя месяца" if len(winners) == 1 else "победителей месяца"
        text = f"Статистика за {month_title}:\n"
        text += f"Поздравляем {winner_label}:\n"
        for winner_id, score in winners:
            name = format_name(winner_id)
            text += f"- {name} — `{score}`\n"

        text += "\nТоп-3 по очкам:\n"
        for place, user_id, score in top_entries:
            name = format_name(user_id)
            text += f"`{place: >2}.` {name} — `{score}`\n"

        summaries.append(text)

    if not summaries:
        return None
    return "\n\n".join(summaries)


def build_previous_year_summary(info, chat_type, chat_id, current_dt, last_run_dt=None, include_all=False):
    def format_name(user_id):
        user = {"first_name": "no_name"}
        if user_id in info.get('detach', {}):
            user = info['detach'][user_id]
        if user_id in info.get('join', {}):
            user = info['join'][user_id]
        return get_name(user=user)

    summaries = []
    if include_all:
        if last_run_dt is None:
            return None
        years = list(range(last_run_dt.year, current_dt.year))
    else:
        year = current_dt.year - 1
        if year < 1:
            return None
        years = [year]

    for year in years:

        history = {}
        data_dir = f"./data/{chat_type}{chat_id}/"
        if not os.path.isdir(data_dir):
            continue

        for filename in os.listdir(data_dir):
            if filename == 'info.json':
                continue
            match = re.search(r'(\d{4})-(\d{2})\.json', filename)
            if not match or int(match.group(1)) != year:
                continue
            file_history = f"{data_dir}{filename}"
            info_history = load(file=file_history)
            if 'top' not in info_history:
                continue
            for k, v in info_history['top'].items():
                history[k] = history.get(k, 0) + v

        if not history:
            continue

        sorted_tuples = sorted(history.items(), key=lambda item: item[1], reverse=True)
        top_score = sorted_tuples[0][1]
        winners = [item for item in sorted_tuples if item[1] == top_score]

        rankings = []
        place = 0
        previous_score = None
        for user_id, score in sorted_tuples:
            if score != previous_score:
                place += 1
                previous_score = score
            rankings.append((place, user_id, score))

        top_entries = [entry for entry in rankings if entry[0] <= 3]
        other_entries = [entry for entry in rankings if entry[0] > 3]

        winner_label = "победителя года" if len(winners) == 1 else "победителей года"
        text = f"Статистика за {year} год:\n"
        text += f"Поздравляем {winner_label}:\n"
        for winner_id, score in winners:
            name = format_name(winner_id)
            text += f"- {name} — `{score}`\n"

        text += "\nТоп-3 по очкам:\n"
        for place, user_id, score in top_entries:
            name = format_name(user_id)
            text += f"`{place: >2}.` {name} — `{score}`\n"

        if other_entries:
            text += "\nОстальные места:\n"
            for place, user_id, score in other_entries:
                name = format_name(user_id)
                text += f"`{place: >2}.` {name} — `{score}`\n"

        summaries.append(text)

    if not summaries:
        return None
    return "\n\n".join(summaries)
