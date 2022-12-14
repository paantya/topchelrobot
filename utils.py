import os
import json
from pathlib import Path

import time, datetime
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
        # print(file_historys)
    else:
        for i in range(period_months):
            year = get_time_dt.year + (get_time_dt.month - i - 1) // 12
            month = (get_time_dt.month - i - 1) % 12 + 1

            file_name = datetime.datetime.strptime(f'{year}-{month}', '%Y-%m').strftime("%Y-%m")
            file_history = f"./data/{type}{message_json['chat']['id']}/{file_name}.json"
            if os.path.exists(file_history):
                file_historys.append(file_history)

    history = {}
    for file_history in file_historys:
        info_history = load(file=file_history)
        if 'top' not in info_history.keys():
            info_history['top'] = {}
        for k,v in info_history['top'].items():
            if k not in history.keys():
                history[k] = 0
            history[k] += v

    if len(history) < 1:
        text =  f"???? ?????????????????? ???????????? ?????? ????????????????????."
        bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                         disable_notification=DISABLE_NOTIFICATION)
        return None
    text = ''
    sorted_tuples = sorted(history.items(), key=lambda item: item[1], reverse=True)
    # ?????? - 10 ?????????????? ???? ?????????????? ??????:
    #
    # ?????????? ???????????????????? ??? 18
    top_score = 0
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
        else:
            break
    total = len(sorted_tuples)
    text =  f"?????????????? ({f'top {top_n}' if not all else 'all'}{since_text}):\n\n{text}\n?????????? ???????????????????? -- {total}"
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
        text += f"*{date_loc_text}:*\n"

        for i, win in enumerate(info_history['win']):
            name = get_name(info, str(win['id']))
            text += f"-- `{win['n']}` {name}\n"
        text += f"\n"

    if len(files) < 1:
        text = f"???? ?????????????????? ???????????? ?????? ????????????????????."
        bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                         disable_notification=DISABLE_NOTIFICATION)
        return None

    text = f"???????????????????? ???? ?????????????????? ????????????:\n{text}"
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)
    return text
