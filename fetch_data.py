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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200: return None
        p = r.json().get('player', {})
        
        # Format Market Value
        val = p.get('proposedMarketValue', 0)
        if val >= 1000000:
            market_str = f"€{val/1000000:.1f}m"
        elif val >= 1000:
            market_str = f"€{val/1000:.0f}k"
        else:
            market_str = "N/A"
        
        return {
            "full_name": p.get('name', 'N/A'),
            "club": p.get('team', {}).get('name', 'N/A'),
            "market_value": market_str,
            "birthday": datetime.fromtimestamp(p.get('dateOfBirthTimestamp', 0)).strftime('%d.%m.%Y') if p.get('dateOfBirthTimestamp') else "N/A",
            "country": p.get('country', {}).get('name', 'N/A'),
            "number": p.get('jerseyNumber', 'N/A')
        }
    except:
        return None

def get_flashscore_stats(flash_id):
    """Fetches deep stats from Flashscore"""
    url = f"https://www.flashscore.com/player/{flash_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-GB,en;q=0.9'
    }
    try:
        time.sleep(random.uniform(5, 8)) # Anti-bot delay
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200: return None
        
        # Strip HTML for regex processing
        text = re.sub('<[^<]+?>', ' ', r.text)
        
        def extract(year):
            if year not in text: 
                return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
            try:
                # Extract chunk after the year
                chunk = text.split(year)[1][:400]
                nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
                if not nums: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
                
                # Check if first number is rating (has a dot)
                i = 0 if "." in nums[0] else -1
                
                return {
                    "rating": nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1] if len(nums) > i+1 else "0",
                    "goals": nums[i+2] if len(nums) > i+2 else "0",
                    "assists": nums[i+3] if len(nums) > i+3 else "0",
                    "yellow": nums[i+4] if len(nums) > i+4 else "0",
                    "red": nums[i+5] if len(nums) > i+5 else "0"
                }
            except:
                return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}

        return {
            "thisSeason": extract("2025/2026"),
            "lastSeason": extract("2024/2025")
        }
    except:
        return None

def main():
    # Set paths relative to script location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    players_path = os.path.join(current_dir, PLAYERS_FILE)
    db_path = os.path.join(current_dir, DB_FILE)
    index_path = os.path.join(current_dir, INDEX_FILE)

    if not os.path.exists(players_path):
        print(f"Error: {PLAYERS_FILE} not found at {players_path}")
        return
        
    with open(players_path, 'r', encoding='utf-8') as f:
        all_players = json.load(f)

    # Load progress index
    start_idx = 0
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r') as f:
                start_idx = int(f.read().strip())
        except: 
            start_idx = 0
    
    if start_idx >= len(all_players): start_idx = 0
    batch = all_players[start_idx:start_idx + BATCH_SIZE]
    
    # Load existing database
    db = {}
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
                print(f"Loaded existing DB with {len(db)} leagues.")
        except Exception as e:
            print(f"Starting with fresh DB. (Reason: {e})")

    timestamp = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")

    processed_count = 0
    for p in batch:
        print(f"Hybrid Fetch: {p['name']}")
        
        # Sofa Header + Flash Stats
        header = get_sofascore_header(p.get('sofa_id'))
        stats = get_flashscore_stats(p.get('flash_id'))
        
        if header and stats:
            league = p.get('league', 'other').lower()
            club = p.get('club', 'unknown').lower()
            
            if league not in db: db[league] = {}
            if club not in db[league]: db[league][club] = {}
            
            db[league][club][p['name'].lower()] = {
                "info": header,
                "stats": stats,
                "last_update": timestamp
            }
            processed_count += 1

    # --- SAVE AND VERIFY ---
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {processed_count} players to {DB_FILE}")
        
        if os.path.exists(db_path):
            print(f"Verification: {DB_FILE} exists. Size: {os.path.getsize(db_path)} bytes.")
    except Exception as e:
        print(f"CRITICAL ERROR WRITING DB: {e}")
    
    # Update index for next batch
    with open(index_path, 'w') as f:
        f.write(str(start_idx + BATCH_SIZE if start_idx + BATCH_SIZE < len(all_players) else 0))

if __name__ == "__main__":
    main()
