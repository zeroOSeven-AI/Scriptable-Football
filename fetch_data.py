import requests
import json
import time
import random
import re
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
BATCH_SIZE = 50 
INDEX_FILE = 'last_index.txt'
DB_FILE = 'master_db.json'
PLAYERS_FILE = 'players.json'

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-GB,en;q=0.9'
    }
    
    try:
        # Anti-bot delay
        time.sleep(random.uniform(5, 8))
        
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200: 
            print(f"Error: Received status {r.status_code} for {player_id}")
            return None
        
        html = r.text
        text_only = re.sub('<[^<]+?>', ' ', html)
        
        # --- DATA EXTRACTION (Automated) ---
        
        # 1. Full Name from meta tag
        name_match = re.search(r'<meta property="og:title" content="([^"]+)">', html)
        full_name = name_match.group(1).split(" - ")[0].replace(" Stats", "").strip() if name_match else "Player"

        # 2. Club (Direct link from HTML)
        club = "N/A"
        club_match = re.search(r'href="/team/[^"]+/">([^<]+)</a>', html)
        if club_match:
            club = club_match.group(1).strip()

        # 3. Market Value
        market_value = "N/A"
        value_match = re.search(r"(€\s?\d+\.?\d*[mKk])", text_only)
        if value_match:
            market_value = value_match.group(1)

        # 4. Nationality
        country = "N/A"
        country_match = re.search(r'participant__country.*?title="(.*?)"', html)
        if country_match:
            country = country_match.group(1).strip()
            
        # 5. Date of Birth
        birthday = "N/A"
        birth_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", text_only)
        if birth_match:
            birthday = birth_match.group(1)

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
            except:
                return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}

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
        print(f"Critical error processing {player_id}: {e}")
        return None

def main():
    if not os.path.exists(PLAYERS_FILE):
        print("Missing players.json")
        return
        
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        all_players = json.load(f)

    # Load progress index
    start_idx = 0
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f:
                start_idx = int(f.read().strip())
        except: start_idx = 0
    
    if start_idx >= len(all_players): start_idx = 0

    end_idx = start_idx + BATCH_SIZE
    current_batch = all_players[start_idx:end_idx]
    
    # Load database
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except: db = {}

    timestamp = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")

    print(f"Starting batch from index {start_idx}...")

    for p in current_batch:
        name_key = p['name'].lower()
        league = p.get('league', 'other').lower()
        club_folder = p.get('club', 'unknown').lower()
        
        print(f"Fetching: {name_key}")
        data = get_player_stats(p['id'])
        
        if data:
            if league not in db: db[league] = {}
            if club_folder not in db[league]: db[league][club_folder] = {}
            
            db[league][club_folder][name_key] = {
                "info": data['info'],
                "stats": data['stats'],
                "last_update": timestamp
            }

    # Save results
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    with open(INDEX_FILE, 'w') as f:
        f.write(str(end_idx if end_idx < len(all_players) else 0))

    print(f"Batch completed. Next run starts from index {end_idx}")

if __name__ == "__main__":
    main()
