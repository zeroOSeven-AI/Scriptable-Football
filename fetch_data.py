import requests
import json
import time
import random
import re
import os

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        time.sleep(random.randint(3, 7))
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
        
        text = re.sub('<[^<]+?>', ' ', response.text)
        
        def extract_season(year):
            parts = text.split(year)
            if len(parts) < 2: return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}
            chunk = parts[1][:300]
            nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
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

# --- GLAVNI DIO ---
def main():
    # Učitavamo tvoj popis od 15+ igrača
    if not os.path.exists('players.json'):
        print("❌ ERROR: players.json ne postoji!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players_list = json.load(f)

    db = {}
    print(f"🚀 Bager kreće na {len(players_list)} igrača...")

    for p in players_list:
        p_id = p['id']
        name = p['name'].lower() # Sprema kao "modric", "livaja"...
        
        print(f"⛏️  Kopam: {name}...")
        stats = get_player_stats(p_id)
        
        if stats:
            # Spremamo DIREKTNO pod ime, bez liga i klubova (najsigurnije)
            db[name] = {
                "header": {
                    "full_name": name.capitalize(),
                    "club": "Football Club",
                    "value": "Check TM"
                },
                "stats": stats,
                "last_update": time.strftime("%H:%M")
            }

    # Spremamo u master_db.json
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("✅ master_db.json je sada PUN podataka!")

if __name__ == "__main__":
    main()
