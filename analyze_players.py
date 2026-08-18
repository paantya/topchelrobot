import json
import re

PIDOR_CHOICE = [
    'Что? Где? Когда? А ты пидор дня - ',
    'Ага! Поздравляю! Сегодня ты пидор - ',
    'Ого, вы посмотрите только! А пидор дня то - ',
    'Ну ты и пидор, ',
    'Пидор дня обыкновенный, 1шт. - ',
    'Кажется, пидор дня - ',
    'Кто бы мог подумать, но пидор дня - ',
    'И прекрасный человек дня сегодня... а нет, ошибка, всего-лишь пидор - ',
    ".∧＿∧",
    'Стоять! Не двигаться! Вы объявлены пидором дня, ',
    'Анализ завершен. Ты пидор, ',
    'Няшный пидор дня - ',
    'Призванный пидор дня - ',
    'Кто тут у нас пидор дня? Ты пидор дня - ',
]

BOT_NAME_TO_ID = {
    "Юра Зорин": "1168337269", "Мария Сорокина": "332059772", "Анастасия Смертина": "297519072",
    "Mарьяна Урусова": "624251840", "Alena": "319687587", "Andrey Kalyagin": "177286141",
    "Dmitriy Bakulin": "364020421", "Ольга Костыря": "1571056372", "Diana Gukova": "453771496",
    "Елена Бреславец": "237519803", "Настасья Михайлова": "466628455", "Кирилл Чичилюк": "877693970",
    "Kolya6": "393521089", "Evgenij Ku": "431802028", "Evgenij Kuvo": "431802028",
    "Глеб Буряк": "384189315", "Ivan Balabanov": "345752278", "Kirill Panchev": "226092459",
    "Dmitry Kladov": "93032925", "Рауана Гавахунова": "6165192816", "Ваня": "196937567",
    "Алексей": "36943651", "Александр Дьяченко": "267970583", "Denis дудник": "502275200",
    "Оленька Лукашева": "634038137", "Кирилл": "226092459", "Krylova Rauana": "6165192816",
    "Mарьяна": "624251840", "Диана": "453771496", "Константин Шварцберг": "504441617"
}

NORMALIZED_NAMES = {
    "1168337269": "Юра Зорин",
    "332059772": "Мария Сорокина (eh_masha)",
    "297519072": "Анастасия Смертина (essenceabsolue)",
    "624251840": "Mарьяна Урусова (mari_annnnna)",
    "319687587": "Alena (daidzina)",
    "177286141": "Andrey Kalyagin (kalyag1n)",
    "364020421": "Dmitriy Bakulin (dimas_202)",
    "1571056372": "Ольга Костыря (Okostyrya)",
    "453771496": "Diana Gukova (DiGukova)",
    "237519803": "Елена Бреславец (Elena_Breslavets)",
    "466628455": "Настасья Михайлова (iamihailova)",
    "877693970": "Кирилл Чичилюк (kiryuha_44)",
    "393521089": "Kolya6 (guchimuchifokyou)",
    "431802028": "Evgenij Ku (evgenijku)",
    "384189315": "Глеб Буряк (Godri5)",
    "345752278": "Ivan Balabanov",
    "226092459": "Kirill Panchev (satan_sucks)",
    "93032925": "Dmitry Kladov",
    "6165192816": "Рауана Гавахунова",
    "196937567": "Ваня (BecTi)",
    "36943651": "Алексей (Aleksei_P)",
    "267970583": "Александр Дьяченко (astralswag)",
    "502275200": "Denis дудник (dudnikd)",
    "634038137": "Оленька Лукашева (olenkalukasheva)",
    "504441617": "Константин Шварцберг",
}

def extract_text(msg_text):
    if isinstance(msg_text, str): return msg_text
    if isinstance(msg_text, list):
        return "".join([p if isinstance(p, str) else p.get('text', '') for p in msg_text])
    return ""

def extract_winner(text):
    for phrase in PIDOR_CHOICE:
        if text.startswith(phrase):
            winner = text[len(phrase):].strip()
            if "ВЖУХ И ТЫ ПИДОР," in text:
                parts = text.split("ВЖУХ И ТЫ ПИДОР,")
                if len(parts) > 1: winner = parts[1].strip()
            winner = re.sub(r' \(@?\w+\)', '', winner)
            return winner.replace('!', '').strip()
    return None

def main():
    with open('notebook/result.json', 'r') as f:
        data = json.load(f)
    
    players = set(BOT_NAME_TO_ID.values())
    # Те, кто когда-либо побеждал или упоминался как победитель
    
    # Отслеживаем состояние по ID
    in_game_ids = set()
    
    # Для сопоставления имен из remove_members с ID
    name_to_id = {v['name']: k for k, v in {} .items()} # Будем наполнять из сообщений
    
    # Сначала наполним name_to_id
    for msg in data.get('messages', []):
        uid = msg.get('from_id', '').replace('user', '')
        name = msg.get('from')
        if uid and name: name_to_id[name] = uid
        
    # Также добавим из BOT_NAME_TO_ID
    for name, uid in BOT_NAME_TO_ID.items():
        name_to_id[name] = uid

    # Хронологический проход
    for msg in data.get('messages', []):
        uid = msg.get('from_id', '').replace('user', '')
        text = extract_text(msg.get('text'))
        
        # Если проявил активность в игре или чате, и он игрок
        if uid in players:
            in_game_ids.add(uid)
            
        winner_name = extract_winner(text)
        if winner_name and winner_name in name_to_id:
            in_game_ids.add(name_to_id[winner_name])
            
        if '/pidoreg' in text and uid:
            in_game_ids.add(uid)
            players.add(uid)

        # Выход из группы
        if msg.get('type') == 'service' and msg.get('action') == 'remove_members':
            for m in msg.get('members', []):
                mid = name_to_id.get(m)
                if not mid:
                    # Попробуем найти по части имени
                    for n, i in name_to_id.items():
                        if m and n and m in n:
                            mid = i
                            break
                if mid:
                    if mid in in_game_ids:
                        in_game_ids.remove(mid)

        # Вход обратно
        if msg.get('type') == 'service' and msg.get('action') in ['join_group_by_link', 'invite_members']:
            new_m = []
            if msg.get('action') == 'join_group_by_link':
                aid = msg.get('actor_id', '').replace('user', '')
                if aid: new_m.append(aid)
            else:
                for m in msg.get('members', []):
                    mid = name_to_id.get(m)
                    if mid: new_m.append(mid)
            for mid in new_m:
                if mid in players:
                    in_game_ids.add(mid)

    # Итоговые списки
    remaining = []
    left = []
    
    for pid in players:
        name = NORMALIZED_NAMES.get(pid, f"Unknown ({pid})")
        if pid in in_game_ids:
            remaining.append(name)
        else:
            left.append(name)
            
    print("=== Участники, которые остаются в игре ===")
    for name in sorted(remaining):
        print(f"- {name}")
        
    print("\n=== Участники, которые вышли из игры ===")
    for name in sorted(left):
        print(f"- {name}")

if __name__ == "__main__":
    main()
