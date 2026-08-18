import json
import os
import re
import argparse
from datetime import datetime
from collections import defaultdict

"""
Скрипт для восстановления истории побед из JSON-экспорта Telegram.
Использует накопленную базу соответствий имен и ID пользователей.

Использование:
    python3 generate_history.py --input notebook/result.json --output data
"""

# Попытка импортировать паттерны из конфига бота, если скрипт в корне
try:
    from config_replay import pidor_choice as CONFIG_PIDOR_CHOICE
except ImportError:
    CONFIG_PIDOR_CHOICE = []

PIDOR_PATTERNS = CONFIG_PIDOR_CHOICE if CONFIG_PIDOR_CHOICE else [
    'Что? Где? Когда? А ты пидор дня - ',
    'Ага! Поздравляю! Сегодня ты пидор - ',
    'Ого, вы посмотрите только! А пидор дня то - ',
    'Ну ты и пидор, ',
    'Пидор дня обыкновенный, 1шт. - ',
    'Кажется, пидор дня - ',
    'Кто бы мог подумать, но пидор дня - ',
    'И прекрасный человек дня сегодня... а нет, ошибка, всего-лишь пидор - ',
    'Стоять! Не двигаться! Вы объявлены пидором дня, ',
    'Анализ завершен. Ты пидор, ',
    'Няшный пидор дня - ',
    'Призванный пидор дня - ',
    'Кто тут у нас пидор дня? Ты пидор дня - ',
    ".∧＿∧",
]

# Маппинг имен, которые использует бот, в Telegram User ID.
# Если в чате появятся новые игроки, их ID нужно будет добавить сюда.
BOT_NAME_TO_ID = {
    "Юра Зорин": "1168337269",
    "Мария Сорокина": "332059772",
    "Анастасия Смертина": "297519072",
    "Mарьяна Урусова": "624251840",
    "Alena": "319687587",
    "Andrey Kalyagin": "177286141",
    "Dmitriy Bakulin": "364020421",
    "Ольга Костыря": "1571056372",
    "Diana Gukova": "453771496",
    "Елена Бреславец": "237519803",
    "Настасья Михайлова": "466628455",
    "Кирилл Чичилюк": "877693970",
    "Kolya6": "393521089",
    "Evgenij Ku": "431802028",
    "Evgenij Kuvo": "431802028",
    "Глеб Буряк": "384189315",
    "Ivan Balabanov": "345752278",
    "Kirill Panchev": "226092459",
    "Dmitry Kladov": "93032925",
    "Рауана Гавахунова": "6165192816",
    "Ваня": "196937567",
    "Алексей": "36943651",
    "Александр Дьяченко": "267970583",
    "Denis дудник": "502275200",
    "Оленька Лукашева": "634038137",
    "Кирилл": "226092459",
    "Krylova Rauana": "6165192816",
    "Mарьяна": "624251840",
    "Диана": "453771496",
}

# Информация о пользователях для info.json
NORMALIZED_USERS = {
    "1168337269": {"first_name": "Юра", "last_name": "Зорин", "username": ""},
    "332059772": {"first_name": "Мария", "last_name": "Сорокина", "username": "eh_masha"},
    "297519072": {"first_name": "Анастасия", "last_name": "Смертина", "username": "essenceabsolue"},
    "624251840": {"first_name": "Mарьяна", "last_name": "Урусова", "username": "mari_annnnna"},
    "319687587": {"first_name": "Alena", "last_name": "", "username": "daidzina"},
    "177286141": {"first_name": "Andrey", "last_name": "Kalyagin", "username": "kalyag1n"},
    "364020421": {"first_name": "Dmitriy", "last_name": "Bakulin", "username": "dimas_202"},
    "1571056372": {"first_name": "Ольга", "last_name": "Костыря", "username": "Okostyrya"},
    "453771496": {"first_name": "Diana", "last_name": "Gukova", "username": "DiGukova"},
    "237519803": {"first_name": "Елена", "last_name": "Бреславец", "username": "Elena_Breslavets"},
    "466628455": {"first_name": "Настасья", "last_name": "Михайлова", "username": "iamihailova"},
    "877693970": {"first_name": "Кирилл", "last_name": "Чичилюк", "username": "kiryuha_44"},
    "393521089": {"first_name": "Kolya6", "last_name": "", "username": "guchimuchifokyou"},
    "431802028": {"first_name": "Evgenij", "last_name": "Ku", "username": "evgenijku"},
    "384189315": {"first_name": "Глеб", "last_name": "Буряк", "username": "Godri5"},
    "345752278": {"first_name": "Ivan", "last_name": "Balabanov", "username": ""},
    "226092459": {"first_name": "Kirill", "last_name": "Panchev", "username": "satan_sucks"},
    "93032925": {"first_name": "Dmitry", "last_name": "Kladov", "username": ""},
    "6165192816": {"first_name": "Рауана", "last_name": "Гавахунова", "username": ""},
    "196937567": {"first_name": "Ваня", "last_name": "", "username": "BecTi"},
    "36943651": {"first_name": "Алексей", "last_name": "", "username": "Aleksei_P"},
    "267970583": {"first_name": "Александр", "last_name": "Дьяченко", "username": "astralswag"},
    "502275200": {"first_name": "Denis", "last_name": "дудник", "username": "dudnikd"},
    "634038137": {"first_name": "Оленька", "last_name": "Лукашева", "username": "olenkalukasheva"},
    "504441617": {"first_name": "Константин", "last_name": "Шварцберг", "username": ""},
}

def extract_text(msg_text):
    if isinstance(msg_text, str):
        return msg_text
    if isinstance(msg_text, list):
        res = ""
        for part in msg_text:
            if isinstance(part, str):
                res += part
            elif isinstance(part, dict) and 'text' in part:
                res += part['text']
        return res
    return ""

def extract_winner(text):
    for phrase in PIDOR_PATTERNS:
        if text.startswith(phrase):
            winner = text[len(phrase):].strip()
            if "ВЖУХ И ТЫ ПИДОР," in text:
                parts = text.split("ВЖУХ И ТЫ ПИДОР,")
                if len(parts) > 1:
                    winner = parts[1].strip()
            # Удаляем юзернейм в скобках, если он есть
            winner = re.sub(r' \(@?\w+\)', '', winner)
            return winner.replace('!', '').strip()
    return None

def process_export(input_file, output_dir):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    print(f"Reading {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    chat_id = data.get('id')
    if not chat_id:
        print("Error: Could not find chat ID in JSON.")
        return

    full_chat_id = int(f"-100{chat_id}") if chat_id > 0 else chat_id
    group_dir = os.path.join(output_dir, f"supergroup{full_chat_id}")
    os.makedirs(group_dir, exist_ok=True)
    
    users = {}
    # Собираем инфо о пользователях из всех сообщений
    for msg in data.get('messages', []):
        for key in ['from_id', 'actor_id']:
            fid = msg.get(key)
            if fid and fid.startswith('user'):
                uid = fid.replace('user', '')
                name = msg.get('from' if key == 'from_id' else 'actor')
                if uid not in users and name:
                    parts = name.split(' ', 1)
                    first = parts[0]
                    last = parts[1] if len(parts) > 1 else ""
                    users[uid] = {"first_name": first, "last_name": last, "username": ""}
    
    # Применяем нормализованные имена для известных пользователей
    for uid, info in NORMALIZED_USERS.items():
        users[uid] = info

    monthly_stats = defaultdict(lambda: {"top": defaultdict(int), "last": None, "win": []})
    
    # Трекинг статуса для info.json.hist
    in_chat = defaultdict(lambda: False)
    registered = defaultdict(lambda: False)
    reg_commands = ['/pidoreg', '/join', '/tauch', '/touch']
    
    # Маппинг для трекинга по именам в сервисных сообщениях
    name_to_uid = {}
    
    # Собираем ВСЕ возможные имена из истории для каждого UID
    for msg in data.get('messages', []):
        for key in ['from_id', 'actor_id']:
            fid = msg.get(key, '')
            if fid.startswith('user'):
                uid = fid.replace('user', '')
                name = msg.get('from' if key == 'from_id' else 'actor')
                if name: name_to_uid[name] = uid
                
    # Добавляем нормализованные и полные имена
    for uid, info in users.items():
        full = f"{info['first_name']} {info['last_name']}".strip()
        name_to_uid[full] = uid
        if info['first_name']:
            name_to_uid[info['first_name']] = uid

    print("Analyzing messages...")
    for msg in data.get('messages', []):
        text = extract_text(msg.get('text'))
        winner_name = extract_winner(text)
        
        # Трекинг присутствия и регистрации
        fid = msg.get('from_id', '')
        uid_msg = fid.replace('user', '') if fid.startswith('user') else None
        
        if uid_msg:
            in_chat[uid_msg] = True
            if any(cmd in text for cmd in reg_commands):
                registered[uid_msg] = True
            if '/detach' in text:
                registered[uid_msg] = False
        
        action = msg.get('action')
        if action == 'remove_members':
            for m_name in msg.get('members', []):
                if isinstance(m_name, str):
                    m_uid = name_to_uid.get(m_name)
                    if not m_uid:
                        for n, u in name_to_uid.items():
                            if m_name in n or n in m_name:
                                m_uid = u; break
                    if m_uid: in_chat[m_uid] = False
        elif action in ['join_group', 'join_group_by_link', 'add_members']:
            for m_name in msg.get('members', []):
                if isinstance(m_name, str):
                    m_uid = name_to_uid.get(m_name)
                    if not m_uid:
                        for n, u in name_to_uid.items():
                            if m_name in n or n in m_name:
                                m_uid = u; break
                    if m_uid: in_chat[m_uid] = True

        if winner_name:
            clean_name = winner_name.replace('!', '').strip()
            uid = None
            
            if clean_name in BOT_NAME_TO_ID:
                uid = BOT_NAME_TO_ID[clean_name]
            
            if not uid:
                uid = name_to_uid.get(clean_name)
            
            if uid:
                # Победитель точно зарегистрирован
                registered[uid] = True
                
                dt = datetime.fromisoformat(msg['date'])
                month_str = dt.strftime("%Y-%m")
                monthly_stats[month_str]["top"][uid] += 1
                monthly_stats[month_str]["last"] = uid
                monthly_stats[month_str]["win"].append({"id": uid, "n": len(monthly_stats[month_str]["win"]) + 1})

    print(f"Saving results to {group_dir}...")
    for month, stats in monthly_stats.items():
        file_path = os.path.join(group_dir, f"{month}.json")
        with open(file_path, 'w') as f:
            json.dump(stats, f, ensure_ascii=False, indent=1)

    # Формирование корректного info.json.hist
    joined_users = {}
    detached_users = {}
    
    # Игроки - те, кто выигрывал или регистрировался
    all_players = set(registered.keys())
    for stats in monthly_stats.values():
        for uid in stats["top"].keys():
            all_players.add(uid)
            
    for uid in all_players:
        if uid in users:
            is_active = in_chat[uid] and registered[uid]
            if is_active:
                joined_users[uid] = users[uid]
            else:
                detached_users[uid] = users[uid]

    with open(os.path.join(group_dir, "info.json"), 'w') as f:
        json.dump({"join": users, "detach": {}}, f, ensure_ascii=False, indent=1)
        
    with open(os.path.join(group_dir, "info.json.hist"), 'w') as f:
        json.dump({"join": joined_users, "detach": detached_users}, f, ensure_ascii=False, indent=1)

    print(f"Done. Generated {len(monthly_stats)} months of history.")
    months = sorted(monthly_stats.keys())
    if months:
        print(f"Period: {months[0]} to {months[-1]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate historical data from Telegram JSON export.')
    parser.add_argument('--input', default='notebook/result.json', help='Path to result.json export')
    parser.add_argument('--output', default='data', help='Output directory (default: data)')
    args = parser.parse_args()
    process_export(args.input, args.output)
