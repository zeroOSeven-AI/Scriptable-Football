import requests
import json
import time
import random
import re

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        time.sleep(random.randint(3, 7))
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
        
        # Čistimo HTML da dobijemo čisti tekst kao u Scriptableu
        text = re.sub('<[^<]+?>', ' ', response.text)
        
        def extract_season(year):
            parts = text.split(year)
            if len(parts) < 2: return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}
            
            # Uzimamo komad teksta nakon godine i tražimo brojeve
            chunk = parts[1][:300]
            # Traži decimale (rating) ili cijele brojeve
            nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
            
            # Ako je prvi broj rating (ima točku), index je 0, inače se pomiče
            i = 0 if (nums and "." in nums[0]) else -1
            
            try:
                return {
                    "rating":  nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1],
                    "goals":   nums[i+2],
                    "assists": nums[i+3],
                    "yellow":  nums[i+4]
                }
            except:
                return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}

        return {
            "thisSeason": extract_season("2025/2026"),
            "lastSeason": extract_season("2024/2025")
        }
    except Exception as e:
        print(f"Greška: {e}")
        return None

# LISTA IGRAČA
players_to_fetch = [
    {"id": "modric-luka/bZWyoJnA", "name": "modric", "league": "serie_a", "club": "ac_milan"},
    {"id": "bellingham-jude/0vgscFU0", "name": "bellingham", "league": "la_liga", "club": "real_madrid"}
]

db = {}
for p in players_to_fetch:
    print(f"Bager kopa: {p['name']}...")
    stats = get_player_stats(p['id'])
    if stats:
        if p['league'] not in db: db[p['league']] = {}
        if p['club'] not in db: db[p['league']][p['club']] = {}
        db[p['league']][p['club']][p['name']] = stats

with open('master_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✅ master_db.json osvježen točnim podacima.")
