import requests
import json
import time
import random
import re
import os

# Točno prema tvojoj slici
PLAYERS_FILE = 'players.json'
DATABASE_FILE = 'master_db.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_stats(text, season_year):
    try:
        parts = text.split(season_year)
        if len(parts) < 2: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0"}
        chunk = parts[1][:300]
        nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
        idx = 0 if (nums and "." in nums[0]) else -1
        return {
            "rating": nums[idx] if idx >= 0 else "0.0",
            "matches": nums[idx+1] if len(nums) > idx+1 else "0",
            "goals": nums[idx+2] if len(nums) > idx+2 else "0",
            "assists": nums[idx+3] if len(nums) > idx+3 else "0"
        }
    except: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0"}

def main():
    # Provjera postoji li file
    if not os.path.exists(PLAYERS_FILE):
        print(f"❌ ERROR: Ne vidim {PLAYERS_FILE} na GitHubu!")
        return

    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Učitaj staru bazu ako postoji, da ne krećemo od nule
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)
    else:
        db = {}

    print(f"🚀 Pokrećem bager za {len(players)} igrača...")

    for p in players:
        name = p['name']
        liga = p['league']
        pid = p['id']
        
        print(f"⛏️  Kopam podatke za: {name}")
        try:
            time.sleep(random.randint(2, 5))
            r = requests.get(f"https://www.flashscore.com/player/{pid}/", headers=HEADERS, timeout=10)
            
            if r.status_code == 200:
                clean_text = re.sub('<[^<]+?>', ' ', r.text)
                
                if liga not in db: db[liga] = {}
                db[liga][name] = {
                    "header": {
                        "full_name": name.replace("-", " ").title(),
                        "club": p.get('club', 'Unknown'),
                        "position": "Player",
                        "value": "Check TM"
                    },
                    "stats": {
                        "thisSeason": extract_stats(clean_text, "2025/2026"),
                        "lastSeason": extract_stats(clean_text, "2024/2025")
                    },
                    "last_update": time.strftime("%H:%M:%S")
                }
            else:
                print(f"⚠️  Flashscore vratio status {r.status_code} za {name}")
        except Exception as e:
            print(f"❌ Greška kod {name}: {e}")

    # Spremi rezultat
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("✅ Sve je spremljeno u master_db.json!")

if __name__ == "__main__":
    main()
