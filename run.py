import random

import telebot
import time, datetime
from random import choice


from config import bot_token
from const import DISABLE_NOTIFICATION, TIME_SHIFT
from utils import load, save, get_name, get_top_list, get_top_statistics
from config_replay import get_opening_remarks
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def send_start(message):
    text = """
Добро пожаловать!
Получить список команд -- /help.
"""
    message_json = message.json
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['help'])
def send_help(message):
    message_json = message.json

    text = """
/topchel - запустить розыгрыш
/start -- запуск бота
/help -- это сообщение
/rules -- правила игры
/join --  вступить в игру
/detach --  выйти из игры
/party (/list)-- список участников
/departy (/delist)-- список бывших участников
/rating (/ratingall) -- рейтинг с начала года
/month (/monthall) -- рейтинг за этот месяц
/year (/yearall) -- то же самое что и /rating
/time (/timeall) -- рейтинг за всё время игры
/statistics (/statisticsall) -- топ месяца
/pidor - запустить розыгрыш пидора
"""
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)

@bot.message_handler(
    commands=[
        'topchel', 'pidor',
        'join', 'detach',
        'rating', 'ratingall',
        'month', 'monthall',
        'quarter', 'quarterall',
        'year', 'yearall',
        'time', 'timeall',
        'party'
    ],
    chat_types=['private', 'channel'])
def send_exit_get_p(message):
    text = "Эта команда для чатов, добавьте бота в группу и вызовите её повторно."
    bot.reply_to(message, text,
                 disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['rules'])
def send_rules(message):
    message_json = message.json
    text = """
*PIDOR GAME!*

Правила игры (только для групповых чатов):
1. Зарегистрируйтесь в игре /join.
2. Запустите розыгрыш по команде /topchel (или /pidor).
3. Просмотреть рейтинг можно с помощью /rating (/ratingall)
4. Просмотреть помесячный рейтинг можно с помощью /statistics (/statisticsall).
5. Описание остальных команд можно найти в /help.
6. Вы великолепны!

Розыгрыш можно запустить раз в сутки, при повторном вызове будет выведен результат предыдущего розыгрыша.

Сброс розогрыша происходит в 3 часа ночи по Москве. 
"""
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)


# @bot.message_handler(commands=['topcheltest', 'pidortest'], chat_types=['group', 'supergroup'])
# def send_topchel_g(message):
#     message_json = message.json
#     bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=8)
#
#     type = message_json['chat']['type']
#     file = f"./data/{type}{message_json['chat']['id']}/info.json"
#     info = load(file=file)
#     join = list(info['join'].keys())
#
#     join_len = len(join)
#     if join_len < 1:
#         bot.reply_to(message,
#                      f"Мало участников в игре ({join_len}), позовите других участников чата вступить в игру нажав /join.",
#                      disable_notification=DISABLE_NOTIFICATION)
#     else:
#         if 'time_last_topchel' in info:
#             time_last_topchel = info['time_last_topchel']
#         else:
#             time_last_topchel = 0
#         time_last_topchel_dt = datetime.datetime.fromtimestamp(time_last_topchel)
#
#         get_time = time.time()
#         get_time_dt = datetime.datetime.fromtimestamp(get_time)
#         if (get_time_dt - time_last_topchel_dt) > TIME_SHIFT:
#             info['time_last_topchel'] = get_time
#             file_name = datetime.datetime.strptime(f'{get_time_dt.year}-{get_time_dt.month}', '%Y-%m').strftime("%Y-%m")
#             file_history = f"./data/{type}{message_json['chat']['id']}/{file_name}.json"
#             info_history = load(file=file_history)
#             if 'top' not in info_history.keys():
#                 info_history['top'] = {}
#
#             id = choice(join)
#             if str(id) not in info_history['top'].keys():
#                 info_history['top'][str(id)] = 0
#             info_history['top'][str(id)] += 1
#             info_history['last'] = str(id)
#             tops_month = sorted(info_history['top'].items(), key=lambda item: item[1], reverse=True)
#             info_history['win'] = []
#             top_n = tops_month[0][1]
#             for t_month in tops_month:
#                 if t_month[1] == top_n:
#                     info_history['win'].append({
#                         "id": t_month[0],
#                         'n': t_month[1]
#                     })
#
#             name = get_name(info, id)
#             init, search, complit, choice_one = get_opening_remarks()
#
#             time.sleep(1)
#             text = f"{init}"
#             bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
#                              disable_notification=DISABLE_NOTIFICATION)
#             time.sleep(2)
#             bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)
#             time.sleep(1)
#             text = f"{search}"
#             bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
#                              disable_notification=DISABLE_NOTIFICATION)
#             time.sleep(2)
#             text = f"{complit}"
#             bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
#                              disable_notification=DISABLE_NOTIFICATION)
#
#             time.sleep(4)
#             bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)
#             time.sleep(1)
#
#             text = f"{choice_one}{name}"
#             bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
#                              disable_notification=DISABLE_NOTIFICATION)
#             save(data=info, file=file)
#             save(data=info_history, file=file_history)
#
#         else:
#             bot.reply_to(message, f"Повтори попытку через {TIME_SHIFT - (get_time_dt - time_last_topchel_dt)} секунд.",
#                          parse_mode='markdown', disable_notification=DISABLE_NOTIFICATION)
#     # bot.reply_to(message, f"All game users id: {join}",
# # 						disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['topchel', 'pidor'], chat_types=['group', 'supergroup'])
def send_topchel_g(message):
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=10)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)
    join = list(info['join'].keys())

    join_len = len(join)
    if join_len < 1:
        bot.reply_to(message,
                     f"Мало участников в игре ({join_len}), позовите других участников чата вступить в игру нажав /join.",
                     disable_notification=DISABLE_NOTIFICATION)
    else:
        if 'time_last_topchel' in info:
            time_last_topchel = info['time_last_topchel']
        else:
            time_last_topchel = 0
        time_last_topchel_dt = datetime.datetime.fromtimestamp(time_last_topchel)

        get_time = time.time()
        get_time_dt = datetime.datetime.fromtimestamp(get_time)
        if get_time_dt.date() != time_last_topchel_dt.date():
            info['time_last_topchel'] = get_time
            file_name = datetime.datetime.strptime(f'{get_time_dt.year}-{get_time_dt.month}', '%Y-%m').strftime("%Y-%m")
            file_history = f"./data/{type}{message_json['chat']['id']}/{file_name}.json"
            info_history = load(file=file_history)
            if 'top' not in info_history.keys():
                info_history['top'] = {}

            id = choice(join)
            if str(id) not in info_history['top'].keys():
                info_history['top'][str(id)] = 0
            info_history['top'][str(id)] += 1
            info_history['last'] = str(id)
            tops_month = sorted(info_history['top'].items(), key=lambda item: item[1], reverse=True)
            info_history['win'] = []
            top_n = tops_month[0][1]
            for t_month in tops_month:
                if t_month[1] == top_n:
                    info_history['win'].append({
                        "id": t_month[0],
                        'n': t_month[1]
                    })

            name = get_name(user=info['join'][id])
            init, search, complit, choice_one = get_opening_remarks()

            time.sleep(1)
            text = f"{init}"
            bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                                   disable_notification=DISABLE_NOTIFICATION)
            time.sleep(2)
            bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)
            time.sleep(1)
            text = f"{search}"
            bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                                   disable_notification=DISABLE_NOTIFICATION)
            time.sleep(2)
            text = f"{complit}"
            bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                                   disable_notification=DISABLE_NOTIFICATION)

            time.sleep(4)
            bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)
            time.sleep(1)

            text = f"{choice_one}{name}"
            bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                                   disable_notification=DISABLE_NOTIFICATION)
            save(data=info, file=file)
            save(data=info_history, file=file_history)

        else:
            file_name = datetime.datetime.strptime(f'{get_time_dt.year}-{get_time_dt.month}', '%Y-%m').strftime("%Y-%m")
            file_history = f"./data/{type}{message_json['chat']['id']}/{file_name}.json"
            info_history = load(file=file_history)
            id = info_history['last']
            name = get_name(info, id)

            text = f"Согласно моей информации, по результатам сегодняшнего розыгрыша пидор дня -- {name}"
            bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                             disable_notification=DISABLE_NOTIFICATION)

    # bot.reply_to(message, f"All game users id: {join}",


# 						disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['join'], chat_types=['group', 'supergroup'])
def send_join_g(message):
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)
    if 'join' not in info.keys():
        info['join'] = {}
    if 'detach' not in info.keys():
        info['detach'] = {}

    if str(message_json['from']['id']) in info['join'].keys():
        bot.reply_to(message, f"Вы уже есть в списке участников игры, выйти --  /detach",
                     disable_notification=DISABLE_NOTIFICATION)
    else:
        info['join'][message_json['from']['id']] = message_json['from']
        info['join'][message_json['from']['id']]['join_ts'] = time.time()
        detach = info['detach'].pop(str(message_json['from']['id']), None)
        save(data=info, file=file)
        if detach is not None:
            bot.reply_to(message, f"Поздравляем с возвращением в игру!\nДля выхода из игры используйте /detach",
                         disable_notification=DISABLE_NOTIFICATION)
        else:
            bot.reply_to(message, f"Поздравляем, теперь вы участвуете в игре!\nДля выхода из игры используйте /detach",
                         disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['detach'], chat_types=['group', 'supergroup'])
def send_detach_g(message):
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)
    if 'join' not in info.keys():
        info['join'] = {}
    if 'detach' not in info.keys():
        info['detach'] = {}

    detach = info['join'].pop(str(message_json['from']['id']), None)
    if detach is not None:
        info['detach'][str(message_json['from']['id'])] = detach
        info['detach'][str(message_json['from']['id'])]['detach_ts'] = time.time()
    save(data=info, file=file)

    if detach is None:
        bot.reply_to(message, f"Вас нет в списке участников игры. Вернуться в игру можно с помощью /join",
                     disable_notification=DISABLE_NOTIFICATION)
    else:
        bot.reply_to(message, f"Теперь вы не участвуете в игре. Вернуться в игру можно с помощью /join",
                     disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['party', 'list'], chat_types=['group', 'supergroup'])
def send_party_g(message):
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)
    if 'join' not in info.keys():
        info['join'] = {}
    if 'detach' not in info.keys():
        info['detach'] = {}

    text = f"Список участников игры ({message_json['chat']['title']} | type: `{message_json['chat']['type']}` | id:`{message_json['chat']['id']}`):"
    sorted_tuples = sorted([int(k) for k in info['join'].keys()])

    for i, id in enumerate(sorted_tuples):
        name = get_name(info, str(id))
        text += f'\n{i + 1}. #ID{id} - {name}'
    bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                     disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['departy', 'delist'], chat_types=['group', 'supergroup'])
def send_departy_g(message):
    message_json = message.json
    bot.send_chat_action(message_json['chat']['id'], action='typing', timeout=5)

    type = message_json['chat']['type']
    file = f"./data/{type}{message_json['chat']['id']}/info.json"
    info = load(file=file)
    if 'join' not in info.keys():
        info['join'] = {}
    if 'detach' not in info.keys():
        info['detach'] = {}

    if len(info['detach'].keys()) < 1:
        text = f"Список бывших участников игры пуст ({message_json['chat']['title']} | type: `{message_json['chat']['type']}` | id:`{message_json['chat']['id']}`)."
        bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                         disable_notification=DISABLE_NOTIFICATION)
    else:
        text = f"Список бывших участников игры ({message_json['chat']['title']} | type: `{message_json['chat']['type']}` | id:`{message_json['chat']['id']}`):"
        sorted_tuples = sorted([int(k) for k in info['detach'].keys()])

        for i, id in enumerate(sorted_tuples):
            name = get_name(info, str(id))
            text += f'\n{i + 1}. #ID{id} - {name}'

        # text = 'Список бывших участников:'
        # for i, key in enumerate(info['detach'].keys()):
        #     name = get_name(user=info['detach'][key])
        #     text += f'\n{i + 1}. {name}'
        bot.send_message(message_json['chat']['id'], text=text, parse_mode='markdown',
                         disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(commands=['month'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_top_list(bot, message, period_months=1, all=False)


@bot.message_handler(commands=['monthall'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_top_list(bot, message, period_months=1, all=True)


# @bot.message_handler(commands=['quarter'], chat_types=['group', 'supergroup'])
# def send_rating_g(message):
#     get_top_list(bot, message, period_months=3, all=False)
#
#
# @bot.message_handler(commands=['quarterall'], chat_types=['group', 'supergroup'])
# def send_rating_g(message):
#     get_top_list(bot, message, period_months=3, all=False)


@bot.message_handler(commands=['rating','year'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_time = time.time()
    get_time_dt = datetime.datetime.fromtimestamp(get_time)
    month = get_time_dt.month
    get_top_list(bot, message, period_months=month, all=False)


@bot.message_handler(commands=['ratingall','yearall'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_time = time.time()
    get_time_dt = datetime.datetime.fromtimestamp(get_time)
    month = get_time_dt.month
    get_top_list(bot, message, period_months=month, all=True)


@bot.message_handler(commands=['time'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_top_list(bot, message, all=False, all_time=True)


@bot.message_handler(commands=['timeall'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_top_list(bot, message, all=True, all_time=True)


@bot.message_handler(commands=['statistics'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_top_statistics(bot, message,  period_months=3, all_time=False)



@bot.message_handler(commands=['statisticsall'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    get_top_statistics(bot, message, all_time=True)



@bot.message_handler(content_types=['new_chat_members'], chat_types=['group', 'supergroup'])
def send_new_chat_members(message):
    message_json = message.json
    if not message_json['new_chat_participant']['is_bot']:
        bot.reply_to(message, "Добро пожаловать!",
                     disable_notification=DISABLE_NOTIFICATION)
    else:
        bot.reply_to(message, "Вы зочем этого железного позвали!?", disable_notification=DISABLE_NOTIFICATION)


@bot.message_handler(content_types=['left_chat_member'], chat_types=['group', 'supergroup'])
def send_rating_g(message):
    message_json = message.json
    if not message_json['left_chat_participant']['is_bot']:
        type = message_json['chat']['type']
        file = f"./data/{type}{message_json['chat']['id']}/info.json"
        info = load(file=file)
        if 'join' not in info.keys():
            info['join'] = {}
        if 'detach' not in info.keys():
            info['detach'] = {}
        if str(message_json['left_chat_participant']['id']) in list(info['join'].keys()):
            detach = info['join'].pop(str(message_json['left_chat_participant']['id']), None)
            if detach is not None:
                info['detach'][str(message_json['from']['id'])] = detach
                info['detach'][str(message_json['from']['id'])]['detach_ts'] = time.time()
            save(data=info, file=file)
            bot.reply_to(message, "Привет, ты чо охуел?\nВыписан из руских и из игры!",
                         disable_notification=DISABLE_NOTIFICATION)
        else:
            bot.reply_to(message, "Привет, ты чо охуел?",
                         disable_notification=DISABLE_NOTIFICATION)
    else:
        bot.reply_to(message, f"Ну и проваливай 8-битный!",
                     disable_notification=DISABLE_NOTIFICATION)

# {
#     'message_id': 571,
#     'from':
#         {
#             'id': 215,
#             'is_bot': False,
#             'first_name': 'Anton',
#             'last_name': 'Pa',
#             'username': 'apa',
#             'language_code': 'en',
#             'is_premium': True
#         },
#     'chat':
#         {
#             'id': -61113,
#             'title': 'pidort',
#             'type': 'group',
#             'all_members_are_administrators': True
#         },
#     'date': 16630,
#     'text': 'ff'
# }


dict_stop_world = {
    'да?': ('да!',
            0.05),
    'da?': ('да!',
            0.1),
    'пидор': ('пидор!',
              0.99),
}



@bot.message_handler(func=lambda message: message.text.split(' ')[0].lower() in dict_stop_world.keys())
def echo_da(message):
    k = message.text.split(' ')[0].lower()
    text, eps = dict_stop_world[k]
    if eps > random.random():
        bot.reply_to(message, text, disable_notification=DISABLE_NOTIFICATION)


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	text = "Для получения списка команд введите /help."
# 	bot.reply_to(message, text, disable_notification=DISABLE_NOTIFICATION)


bot.infinity_polling()
