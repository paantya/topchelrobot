import telebot
from utils import load, save, get_name

from random import choice
from config import bot_token
import time


bot = telebot.TeleBot(bot_token)
# migrate_from_chat_id
# https://pytba.readthedocs.io/en/latest/index.html
# https://pytba.readthedocs.io/en/latest/sync_version/index.html?highlight=get_chat_member#telebot.TeleBot.get_chat_member
# @bot.message_handler(content_types=['new_chat_members'])
#Client.get_chat_members()
# from pyrogram import enums
#
# # Get members
# async for member in app.get_chat_members(chat_id):
#     print(member)


# from pyrogram import Client


# app = Client(
# 	"my_bot",
# 	api_id=api_id, api_hash=api_hash,
# 	bot_token=bot_token,
#
# )
#
# app.start()
# for member in app.get_chat_members(message_json['chat']['id']):
# # print(member)
# 	bot.reply_to(message, f"Ты {member}")
# app.stop()
# app.



@bot.message_handler(commands=['stpip3 install -U uvloopart'])
def send_start(message):
	text = """
Добро пожаловать!
Для получения списка команд введите /help
"""
	bot.reply_to(message, text)


@bot.message_handler(commands=['help'])
def send_help(message):
	text = """
/topchel - выбираем топового чела
/start -- запуск бота
/help -- это сообщение
/rules -- правила игры
/join --  принять участие в игре
/detach --  перестать участвовать в игре
/party (/list)-- список участников
/departy (/delist)-- список бывших участников
/rating (/ratingall) -- рейтинг "топ 10" (для всех)
/month (/monthall) -- рейтинг за месяц
/quarter (/quarterall) -- рейтинг за 3 месяца
/year (/yearall) -- рейтинг за год
/pidor - выбираем пидора
	"""
	bot.reply_to(message, f"{text}")



@bot.message_handler(
	commands=[
		'topchel', 'pidor',
		'join', 'detach',
		'rating', 'ratingall',
		'month', 'monthall',
		'quarter', 'quarterall',
		'year', 'yearall',
		'party'
	],
	chat_types=['private', 'channel'])
def send_join_p(message):
	text = "Эта команда для чатов, добавьте бота в группу и вызовите эту команду повторно в группе."
	bot.reply_to(message, text)


@bot.message_handler(commands=['rules'])
def send_rules(message):
	text = """
	*PIDOR GAME!*

	Правила игры:
	1. Добавляете бота в групповой чат.
	2. Добавляете бота в админы чата, что бы бот мог видеть список участников.
	3. В чате, игроки добавляются в игру, с помощью /join
	4. В чате, участники игры запускают выбор /topchel (или pidor) раз в сутки. Счётчик сбрасывается в 3 часа ночи.
	5. Просмотреть рейтинг можно с помощью /rating 

		"""
	bot.reply_to(message, text, parse_mode='markdown')

@bot.message_handler(commands=['topchel', 'pidor'],	chat_types=['group', 'supergroup'])
def send_topchel_g(message):
	message_json = message.json


	type = message_json['chat']['type']
	file = f"./data/{type}{message_json['chat']['id']}/info.json"
	info = load(file=file)
	join = list(info['join'].keys())

	join_len = len(join)
	if join_len < 1:
		bot.reply_to(message, f"Мало участников в игре ({join_len}), позовите других участников чата вступить в игру нажав /join.")
	else:
		id = choice(join)
		name = get_name(info['join'][id])
		bot.reply_to(message, f"Отличился сегодня: \n{name}", parse_mode='markdown')
		# bot.reply_to(message, f"All game users id: {join}")


@bot.message_handler(
	commands=[
		'topchel', 'pidor',
	],
	chat_types=['private', 'channel'])
def send_topchel_p(message):
	text = "Эта команда для чатов, добавьте бота в группу и вызовите эту команду повторно в группе."
	bot.reply_to(message, text)



@bot.message_handler(commands=['join'],	chat_types=['group', 'supergroup'])
def send_join_g(message):
	message_json = message.json
	type = message_json['chat']['type']
	file = f"./data/{type}{message_json['chat']['id']}/info.json"
	info = load(file=file)
	if 'join' not in info.keys():
		info['join'] = {}
	if 'detach' not in info.keys():
		info['detach'] = {}

	if str(message_json['from']['id']) in info['join'].keys():
		bot.reply_to(message, f"Вы уже есть в списке участников в игры.")
	else:
		info['join'][message_json['from']['id']] = message_json['from']
		info['join'][message_json['from']['id']]['join_ts'] = time.time()
		detach = info['detach'].pop(str(message_json['from']['id']), None)
		save(data=info, file=file)
		if detach is not None:
			bot.reply_to(message, f"Поздравляем с возвращением в игру!\nДля выхода из игры используйте /detach.")
		else:
			bot.reply_to(message, f"Поздравляем, теперь вы участвуете в игре!\nДля выхода из игры используйте /detach.")


@bot.message_handler(commands=['detach'],chat_types=['group', 'supergroup'])
def send_detach_g(message):
	message_json = message.json
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
		bot.reply_to(message, f"Вас нет в списке участников игры.  Вернуться в игру можно с помощью /join")
	else:
		bot.reply_to(message, f"Теперь вы не участвуете в игре. Вернуться в игру можно с помощью /join")


@bot.message_handler(commands=['party', 'list'], chat_types=['group', 'supergroup'])
def send_party_g(message):
	message_json = message.json
	type = message_json['chat']['type']
	file = f"./data/{type}{message_json['chat']['id']}/info.json"
	info = load(file=file)
	if 'join' not in info.keys():
		info['join'] = {}
	if 'detach' not in info.keys():
		info['detach'] = {}

	text = 'Список участников:'
	for i, key in enumerate(info['join'].keys()):
		name = get_name(info['join'][key])
		text += f'\n{i+1}. {name}'
	bot.reply_to(message, text, parse_mode='markdown')

@bot.message_handler(commands=['departy', 'delist'], chat_types=['group', 'supergroup'])
def send_departy_g(message):
	message_json = message.json
	type = message_json['chat']['type']
	file = f"./data/{type}{message_json['chat']['id']}/info.json"
	info = load(file=file)
	if 'join' not in info.keys():
		info['join'] = {}
	if 'detach' not in info.keys():
		info['detach'] = {}

	if len(info['detach'].keys()) < 1:
		bot.reply_to(message, "Список бывших участников пуст.", parse_mode='markdown')
	else:
		text = 'Список бывших участников:'
		for i, key in enumerate(info['detach'].keys()):
			name = get_name(info['detach'][key])
			text += f'\n{i+1}. {name}'
		bot.reply_to(message, text, parse_mode='markdown')


@bot.message_handler(
	commands=[
		'rating', 'ratingall',
		'month', 'monthall',
		'quarter', 'quarterall',
		'year', 'yearall',
	],
	chat_types=['group', 'supergroup'])
def send_rating_g(message):
	message_json = message.json
	bot.reply_to(message, "рейтинг ещё не считается")


@bot.message_handler(content_types=['new_chat_members'], chat_types=['group', 'supergroup'])
def send_new_chat_members(message):
	message_json = message.json
	if not message_json['new_chat_participant']['is_bot']:
		bot.reply_to(message, "Добро пожаловать!")
	else:
		bot.reply_to(message, "Вы зочем этого железного позвали!?")


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
			bot.reply_to(message, "Пока, ты больше не участвуешь в игре!")
		else:
			bot.reply_to(message, "Счастья, здоровья, удачи!")
	else:
		bot.reply_to(message, f"Ну и проваливай железяка!")


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	text = "Для получения списка команд введите /help."
# 	bot.reply_to(message, str(message.json))


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	text = "Для получения списка команд введите /help."
# 	bot.reply_to(message, text)


bot.infinity_polling()