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
    """Fetches clean profile data from Sofascore API"""
    # Koristimo pravi mobilni API endpoint koji je stabilniji
    url = f"https://api.sofascore.com/api/v1/player/{sofa_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Cache-Control': 'no-cache'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200: 
            print(f"  ! Sofa API Error ({r.status_code}) for ID: {sofa_id}")
            return None
        
        p = r.json().get('player', {})
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
    except Exception as e:
        print(f"  ! Sofa Exception: {e}")
        return None

def get_flashscore_stats(flash_id):
    """Fetches deep stats from Flashscore via scraping"""
    url = f"https://www.flashscore.com/player/{flash_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        time.sleep(random.uniform(3, 5))
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

        return {"thisSeason": extract("2025/2026"), "lastSeason": extract("2024/2025")}
    except: return None

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    players_path = os.path.join(current_dir, PLAYERS_FILE)
    db_path = os.path.join(current_dir, DB_FILE)
    
    if not os.path.exists(players_path): return
    with open(players_path, 'r', encoding='utf-8') as f: all_players = json.load(f)

    db = {} # Start fresh if needed
    timestamp = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")
    processed_count = 0

    for p in all_players: # Maknuo sam batching privremeno da sve odradi odmah
        print(f"Hybrid Fetch: {p['name']}")
        
        header = get_sofascore_header(p.get('sofa_id'))
        stats = get_flashscore_stats(p.get('flash_id'))
        
        # Čak i ako Flashscore ne vrati stats, uzmi bar Sofa Header
        if header:
            league = p.get('league', 'other').lower()
            club = p.get('club', 'unknown').lower()
            if league not in db: db[league] = {}
            if club not in db[league]: db[league][club] = {}
            
            db[league][club][p['name'].lower()] = {
                "info": header,
                "stats": stats if stats else {},
                "last_update": timestamp
            }
            processed_count += 1
            print(f"  -> Success: {p['name']}")

    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved {processed_count} players.")

if __name__ == "__main__":
    main()
