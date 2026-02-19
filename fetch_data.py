import requests
import json
import time
import random
import re
import os
from datetime import datetime, timedelta

# --- POSTAVKE ---
BATCH_SIZE = 50 
INDEX_FILE = 'last_index.txt'
DB_FILE = 'master_db.json'
PLAYERS_FILE = 'players.json'

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        time.sleep(random.uniform(7, 12))
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200: return None
        
        html = response.text
        # Čistimo tekst za statistiku, ali čuvamo HTML za header
        text_only = re.sub('<[^<]+?>', ' ', html)
        
        # --- EKSTRAKCIJA HEADER PODATAKA (Kao Scriptable) ---
        
        # 1. Puno Ime (iz naslova stranice)
        name_match = re.search(r"<title>(.*?) - Flashscore", html)
        full_name = name_match.group(1).replace(" Stats", "").strip() if name_match else "Igrač"

        # 2. Klub (Tražimo link koji sadrži /team/)
        club_match = re.search(r'href="/team/[^"]+">([^<]+)</a>', html)
        club = club_match.group(1).strip() if club_match else "Nepoznato"

        # 3. Market Value (Tražimo € i broj)
        value_match = re.search(r"(€\s?\d+\.?\d*[mKk])", text_only)
        market_value = value_match.group(1) if value_match else "N/A"
            
        # 4. Zemlja i Rođendan
        country_match = re.search(r'Nationality:</span>\s*<span>([^<]+)</span>', html)
        country = country_match.group(1).strip() if country_match else "N/A"
        
        birth_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", text_only)
        birthday = birth_match.group(1) if birth_match else "N/A"

        def extract_season(year):
            if year not in text_only: 
                return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
            try:
                parts = text_only.split(year)
                chunk = parts[1][:400]
                nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
                if not nums: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
                i = 0 if "." in nums[0] else -1
                return {
                    "rating":  nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1] if len(nums) > i+1 else "0",
                    "goals":   nums[i+2] if len(nums) > i+2 else "0",
                    "assists": nums[i+3] if len(nums) > i+3 else "0",
                    "yellow":  nums[i+4] if len(nums) > i+4 else "0",
                    "red":     nums[i+5] if len(nums) > i+5 else "0"
                }
            except: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}

        return {
            "info": {
                "full_name": full_name,
                "club": club,
                "market_value": market_value,
                "birthday": birthday,
                "country": country
            },
            "stats": {
                "thisSeason": extract_season("2025/2026"),
                "lastSeason": extract_season("2024/2025")
            }
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    if not os.path.exists(PLAYERS_FILE): return
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        all_players = json.load(f)

    start_idx = 0
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f: start_idx = int(f.read().strip())
        except: start_idx = 0
    
    if start_idx >= len(all_players): start_idx = 0
    end_idx = start_idx + BATCH_SIZE
    current_batch = all_players[start_idx:end_idx]
    
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content: db = json.loads(content)
        except: db = {}

    hr_vrijeme = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")

    for p in current_batch:
        name_key = p['name'].lower()
        liga = p.get('league', 'ostalo').lower()
        klub = p.get('club', 'nepoznato').lower()
        
        print(f"⛏️  Kopam: {name_key}...")
        data = get_player_stats(p['id'])
        
        if data:
            if liga not in db: db[liga] = {}
            if klub not in db[liga]: db[liga][klub] = {}
            
            db[liga][klub][name_key] = {
                "header": data['info'],
                "stats": data['stats'],
                "last_update": hr_vrijeme
            }

    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    with open(INDEX_FILE, 'w') as f:
        f.write(str(end_idx if end_idx < len(all_players) else 0))

if __name__ == "__main__":
    main()
