import json
import re
import argparse
from datetime import datetime
from collections import defaultdict

"""
Скрипт для анализа истории чата и формирования списков игроков:
1. Те, кто остаются в игре (находятся в чате или вернулись после выхода).
2. Те, кто вышли из игры (покинули чат и не возвращались).

Использование:
    python3 check_players_status.py --input notebook/result.json
"""

# Маппинг имен и ID для нормализации (из generate_history.py)
NORMALIZED_USERS = {
    "1168337269": {"name": "Юра Зорин", "username": ""},
    "332059772": {"name": "Мария Сорокина (eh_masha)", "username": "eh_masha"},
    "297519072": {"name": "Анастасия Смертина (essenceabsolue)", "username": "essenceabsolue"},
    "624251840": {"name": "Mарьяна Урусова (mari_annnnna)", "username": "mari_annnnna"},
    "319687587": {"name": "Alena (daidzina)", "username": "daidzina"},
    "177286141": {"name": "Andrey Kalyagin (kalyag1n)", "username": "kalyag1n"},
    "364020421": {"name": "Dmitriy Bakulin (dimas_202)", "username": "dimas_202"},
    "1571056372": {"name": "Ольга Костыря (Okostyrya)", "username": "Okostyrya"},
    "453771496": {"name": "Diana Gukova (DiGukova)", "username": "DiGukova"},
    "237519803": {"name": "Елена Бреславец (Elena_Breslavets)", "username": "Elena_Breslavets"},
    "466628455": {"name": "Настасья Михайлова (iamihailova)", "username": "iamihailova"},
    "877693970": {"name": "Кирилл Чичилюк (kiryuha_44)", "username": "kiryuha_44"},
    "393521089": {"name": "Kolya6 (guchimuchifokyou)", "username": "guchimuchifokyou"},
    "431802028": {"name": "Evgenij Ku (evgenijku)", "username": "evgenijku"},
    "384189315": {"name": "Глеб Буряк (Godri5)", "username": "Godri5"},
    "345752278": {"name": "Ivan Balabanov", "username": ""},
    "226092459": {"name": "Kirill Panchev (satan_sucks)", "username": "satan_sucks"},
    "93032925": {"name": "Dmitry Kladov", "username": ""},
    "6165192816": {"name": "Рауана Гавахунова", "username": ""},
    "196937567": {"name": "Ваня (BecTi)", "username": "BecTi"},
    "36943651": {"name": "Алексей (Aleksei_P)", "username": "Aleksei_P"},
    "267970583": {"name": "Александр Дьяченко (astralswag)", "username": "astralswag"},
    "502275200": {"name": "Denis дудник (dudnikd)", "username": "dudnikd"},
    "634038137": {"name": "Оленька Лукашева (olenkalukasheva)", "username": "olenkalukasheva"},
    "272067069": {"name": "Илья Андреевич Кашников (cash_ilya)", "username": "cash_ilya"},
    "314283941": {"name": "Galina Krasova", "username": ""},
    "504441617": {"name": "Константин Шварцберг", "username": ""},
    "829939434": {"name": "Артём (fobosartem)", "username": "fobosartem"},
}

PIDOR_PATTERNS = [
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

def get_text(msg):
    t = msg.get('text', '')
    if isinstance(t, list):
        res = ''
        for p in t:
            if isinstance(p, str): res += p
            elif isinstance(p, dict): res += p.get('text', '')
        return res
    return str(t)

def extract_winner(text):
    for phrase in PIDOR_PATTERNS:
        if text.startswith(phrase):
            winner = text[len(phrase):].strip()
            if "ВЖУХ И ТЫ ПИДОР," in text:
                parts = text.split("ВЖУХ И ТЫ ПИДОР,")
                if len(parts) > 1: winner = parts[1].strip()
            winner = re.sub(r' \(@?\w+\)', '', winner)
            return winner.replace('!', '').strip()
    return None

def analyze_status(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # 1. Сбор всех имен и маппинг в UID
    name_to_uid = {}
    uid_to_name = {}
    for uid, info in NORMALIZED_USERS.items():
        name_to_uid[info['name']] = uid
        uid_to_name[uid] = info['name']

    # Дополнительный маппинг из истории сообщений
    for msg in data.get('messages', []):
        for key in ['from_id', 'actor_id']:
            fid = msg.get(key, '')
            if fid.startswith('user'):
                uid = fid.replace('user', '')
                name = msg.get('from' if key == 'from_id' else 'actor')
                if name: name_to_uid[name] = uid
                if uid not in uid_to_name and name: uid_to_name[uid] = name

    # 2. Определение игроков (те, кто когда-либо регистрировался или выигрывал)
    players = set()
    registration_commands = ['/pidoreg', '/join', '/tauch', '/touch']
    
    for msg in data.get('messages', []):
        text = get_text(msg)
        
        # Проверка команд регистрации
        if any(cmd in text for cmd in registration_commands):
            fid = msg.get('from_id', '')
            if fid.startswith('user'): players.add(fid.replace('user', ''))
        
        # Победитель точно является игроком
        winner = extract_winner(text)
        if winner:
            uid = name_to_uid.get(winner)
            if not uid:
                # Поиск частичного совпадения
                for n, u in name_to_uid.items():
                    if n and (winner in n or n in winner):
                        uid = u; break
            if uid: players.add(uid)

    # Добавляем 829939434 в список игроков, так как он точно регистрировался
    players.add('829939434')

    # 3. Отслеживание статуса (хронологически)
    in_chat = defaultdict(lambda: False)
    registered = defaultdict(lambda: False)
    
    # Для тех, кто победил в розыгрыше, мы знаем, что они были зарегистрированы на тот момент
    for msg in data.get('messages', []):
        text = get_text(msg)
        action = msg.get('action')
        fid = msg.get('from_id', '')
        uid = fid.replace('user', '') if fid.startswith('user') else None
        
        # Сообщения от пользователя означают, что он в чате
        if uid and uid in players:
            in_chat[uid] = True
            
            # Если это команда регистрации
            if any(cmd in text for cmd in registration_commands):
                registered[uid] = True
            
            # Если это команда выхода
            if '/detach' in text:
                registered[uid] = False

        # Победитель розыгрыша (бот подтверждает регистрацию)
        winner = extract_winner(text)
        if winner:
            w_uid = name_to_uid.get(winner)
            if not w_uid:
                for n, u in name_to_uid.items():
                    if n and (winner in n or n in winner):
                        w_uid = u; break
            if w_uid and w_uid in players:
                registered[w_uid] = True

        # Сервисные сообщения о входе/выходе из чата
        if action == 'remove_members':
            for m_name in msg.get('members', []):
                if not isinstance(m_name, str): continue
                m_uid = name_to_uid.get(m_name)
                if not m_uid:
                    for n, u in name_to_uid.items():
                        if isinstance(n, str) and (m_name in n or n in m_name):
                            m_uid = u; break
                if m_uid and m_uid in players:
                    in_chat[m_uid] = False
        
        elif action in ['join_group', 'join_group_by_link', 'add_members']:
            for m_name in msg.get('members', []):
                if not isinstance(m_name, str): continue
                m_uid = name_to_uid.get(m_name)
                if not m_uid:
                    for n, u in name_to_uid.items():
                        if isinstance(n, str) and (m_name in n or n in m_name):
                            m_uid = u; break
                if m_uid and m_uid in players:
                    in_chat[m_uid] = True

    # 4. Формирование списков
    in_game = []
    out_game = []
    
    bots = ['Sublime Bot', 'Topchel', '1802528751', '232117096']
    
    for uid in sorted(players):
        name = NORMALIZED_USERS.get(uid, {}).get('name', uid_to_name.get(uid, uid))
        if name in bots or uid in bots: continue
        
        # Пользователь в игре, если он и в чате, и зарегистрирован
        is_active = in_chat[uid] and registered[uid]
        
        if is_active:
            in_game.append(name)
        else:
            out_game.append(name)

    print("\n✅ В ИГРЕ (ОСТАЮТСЯ ИЛИ ВЕРНУЛИСЬ):")
    for name in sorted(set(in_game)):
        print(f"  - {name}")

    print("\n❌ ВЫШЛИ ИЗ ИГРЫ (НЕ ВЕРНУЛИСЬ):")
    for name in sorted(set(out_game)):
        print(f"  - {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze player status from Telegram history.')
    parser.add_argument('--input', default='notebook/result.json', help='Path to result.json')
    args = parser.parse_args()
    analyze_status(args.input)
