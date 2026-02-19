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

def get_sofascore_header(sofa_id):
    """Fetches clean profile data from Sofascore"""
    url = f"https://api.sofascore.com/api/v1/player/{sofa_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200: return None
        p = r.json().get('player', {})
        
        # Format Market Value
        val = p.get('proposedMarketValue', 0)
        market_str = f"€{val/1000000:.1f}m" if val >= 1000000 else f"€{val/1000:.0f}k" if val > 0 else "N/A"
        
        return {
            "full_name": p.get('name', 'N/A'),
            "club": p.get('team', {}).get('name', 'N/A'),
            "market_value": market_str,
            "birthday": datetime.fromtimestamp(p.get('dateOfBirthTimestamp', 0)).strftime('%d.%m.%Y') if p.get('dateOfBirthTimestamp') else "N/A",
            "country": p.get('country', {}).get('name', 'N/A'),
            "number": p.get('jerseyNumber', 'N/A')
        }
    except: return None

def get_flashscore_stats(flash_id):
    """Fetches deep stats from Flashscore"""
    url = f"https://www.flashscore.com/player/{flash_id}/"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-GB,en;q=0.9'}
    try:
        time.sleep(random.uniform(4, 6))
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200: return None
        
        text = re.sub('<[^<]+?>', ' ', r.text)
        
        def extract(year):
            if year not in text: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
            try:
                chunk = text.split(year)[1][:400]
                nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
                i = 0 if "." in nums[0] else -1
                return {
                    "rating": nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1] if len(nums) > i+1 else "0",
                    "goals": nums[i+2] if len(nums) > i+2 else "0",
                    "assists": nums[i+3] if len(nums) > i+3 else "0",
                    "yellow": nums[i+4] if len(nums) > i+4 else "0",
                    "red": nums[i+5] if len(nums) > i+5 else "0"
                }
            except: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}

        return {
            "thisSeason": extract("2025/2026"),
            "lastSeason": extract("2024/2025")
        }
    except: return None

def main():
    if not os.path.exists(PLAYERS_FILE): return
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f: all_players = json.load(f)

    start_idx = 0
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f: start_idx = int(f.read().strip())
        except: start_idx = 0
    
    if start_idx >= len(all_players): start_idx = 0
    batch = all_players[start_idx:start_idx + BATCH_SIZE]
    
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f: db = json.load(f)
        except: db = {}

    ts = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")

    for p in batch:
        print(f"Hybrid Fetch: {p['name']}")
        
        # Step 1: Sofa Header
        header = get_sofascore_header(p.get('sofa_id'))
        # Step 2: Flash Stats
        stats = get_flashscore_stats(p.get('flash_id'))
        
        if header and stats:
            league = p.get('league', 'other').lower()
            club = p.get('club', 'unknown').lower()
            if league not in db: db[league] = {}
            if club not in db[league]: db[league][club] = {}
            
            db[league][club][p['name'].lower()] = {
                "header": header,
                "stats": stats,
                "last_update": ts
            }

    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    with open(INDEX_FILE, 'w') as f:
        f.write(str(start_idx + BATCH_SIZE if start_idx + BATCH_SIZE < len(all_players) else 0))

if __name__ == "__main__":
    main()
