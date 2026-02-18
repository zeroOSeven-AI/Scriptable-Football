import requests
import json
import time
import random
import re
import os

# --- PUTANJE ---
# Koristimo apsolutne putanje da GitHub ne bi lutao
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYERS_FILE = os.path.join(BASE_DIR, 'players.json')
DATABASE_FILE = os.path.join(BASE_DIR, 'master_db.json')

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

def run_bager():
    if not os.path.exists(PLAYERS_FILE):
        print(f"❌ File {PLAYERS_FILE} ne postoji!")
        return

    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        players_list = json.load(f)

    # Učitaj staru bazu ako postoji
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            master_db = json.load(f)
    else:
        master_db = {}

    for p in players_list:
        name = p.get('name', 'unknown')
        liga = p.get('league', 'others')
        pid = p.get('id')
        
        if not pid: continue
        
        print(f"⛏️  Kopam: {name}...")
        try:
            time.sleep(random.randint(2, 5))
            r = requests.get(f"https://www.flashscore.com/player/{pid}/", headers=HEADERS, timeout=10)
            if r.status_code != 200: continue
            
            clean_text = re.sub('<[^<]+?>', ' ', r.text)
            
            if liga not in master_db: master_db[liga] = {}
            master_db[liga][name] = {
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
        except Exception as e:
            print(f"⚠️ Preskačem {name} zbog greške: {e}")

    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("✅ Gotovo!")

if __name__ == "__main__":
    run_bager()
