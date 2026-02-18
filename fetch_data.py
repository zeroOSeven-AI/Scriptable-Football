import requests
import json
import time
import random
import re

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    
    try:
        # Pauza da nas ne blokiraju
        time.sleep(random.randint(5, 10))
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        text = response.text
        
        # Regex za čupanje golova i asista iz SUMMARY bloka (prilagođeno tvojoj strukturi)
        # Tražimo sezonu 2025/2026 i brojeve iza nje
        pattern = r"2025/2026.*?([\d\.]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            return {
                "rating": match.group(1),
                "matches": match.group(2),
                "goals": match.group(3),
                "assists": match.group(4),
                "yellow": match.group(5)
            }
    except Exception as e:
        print(f"Greška za {player_id}: {e}")
    return None

# POPIS IGRAČA (Struktura koju si tražio)
players_to_fetch = [
    {"id": "modric-luka/bZWyoJnA", "name": "modric", "league": "serie_a", "club": "ac_milan"},
    {"id": "bellingham-jude/0vgscFU0", "name": "bellingham", "league": "la_liga", "club": "real_madrid"}
]

db = {}

for p in players_to_fetch:
    print(f"Kopam za: {p['name']}...")
    stats = get_player_stats(p['id'])
    if stats:
        if p['league'] not in db: db[p['league']] = {}
        if p['club'] not in db: db[p['league']][p['club']] = {}
        db[p['league']][p['club']][p['name']] = stats

# Spremanje u file
with open('master_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✅ master_db.json je uspješno kreiran.")
