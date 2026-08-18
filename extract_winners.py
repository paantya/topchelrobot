import json
import re
from collections import defaultdict

def extract_text(msg_text):
    if isinstance(msg_text, str):
        return msg_text
    if isinstance(msg_text, list):
        res = ''
        for part in msg_text:
            if isinstance(part, str):
                res += part
            elif isinstance(part, dict) and 'text' in part:
                res += part['text']
        return res
    return ''

def analyze_winners():
    path = 'notebook/log/result.json'
    with open(path, 'r') as f:
        data = json.load(f)
    
    messages = data.get('messages', [])
    chat_winners = defaultdict(set)
    
    pidor_choice = [
        'Что? Где? Когда? А ты пидор дня - ',
        'Ага! Поздравляю! Сегодня ты пидор - ',
        'Ого, вы посмотрите только! А пидор дня то - ',
        'Ну ты и пидор, ',
        'Пидор дня обыкновенный, 1шт. - ',
        'Кажется, пидор дня - ',
        'Кто бы мог подумать, но пидор дня - ',
        'И прекрасный человек дня сегодня... а нет, ошибка, всего-лишь пидор - ',
        'ВЖУХ И ТЫ ПИДОР, ',
        'Стоять! Не двигаться! Вы объявлены пидором дня, ',
        'Анализ завершен. Ты пидор, ',
        'Няшный пидор дня - ',
        'Призванный пидор дня - ',
        'Кто тут у нас пидор дня? Ты пидор дня - ',
    ]
    
    chat_names = {
        '-1001674536042': 'Походское',
        '-1001772934533': 'Карыч',
        '-1001171212951': 'Казино "Тухлая сельдь"',
        '1717789783': 'pidortest',
        '-1001717789783': 'pidortest'
    }

    for m in messages:
        text = extract_text(m.get('text'))
        if not text: continue
        
        # 1. INFO logs
        if 'INFO' in text:
            # INFO -- pidortest (supergroup -1001717789783) -- win Alena (daidzina) (id: 319687587)
            if 'win' in text:
                gid_match = re.search(r'supergroup\s*(-?\d+)', text)
                win_match = re.search(r'win\s+(.*?)\s+\(id:', text)
                if gid_match and win_match:
                    gid = gid_match.group(1)
                    winner = win_match.group(1).strip()
                    chat_winners[gid].add(winner)
                    continue

            # INFOsupergroup`-1001674536042`*Походское* Andrey Kalyagin (kalyag1n) (id: 177286141)
            if 'INFOsupergroup' in text:
                gid_match = re.search(r'supergroup\s*`(-?\d+)`', text)
                if gid_match:
                    gid = gid_match.group(1)
                    # Find winner after chat name
                    parts = text.split('*')
                    if len(parts) >= 3:
                         win_part = parts[2].split('(id:')[0].strip()
                         if win_part:
                             chat_winners[gid].add(win_part)
                             continue

        # 2. Local wins (pidortest)
        for pattern in pidor_choice:
            if pattern in text:
                parts = text.split(pattern)
                if len(parts) > 1:
                    winner = parts[1].split('!')[0].split('\n')[0].strip()
                    chat_winners['1717789783'].add(winner)
                break

    for gid in sorted(chat_winners.keys()):
        winners = chat_winners[gid]
        name = chat_names.get(gid, gid)
        print(f'\n--- {name} (ID: {gid}) ---')
        for w in sorted(list(winners)):
            print(f'- {w}')

if __name__ == "__main__":
    analyze_winners()
