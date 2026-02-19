import requests
import json
import time
import random
import re
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DB_FILE = 'master_db.json'
PLAYERS_FILE = 'players.json'

def get_flashscore_stats(flash_id):
    """Čisti scraping Flashscore-a za deep stats"""
    url = f"https://www.flashscore.com/player/{flash_id}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        time.sleep(random.uniform(2, 4))
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

    db = {}
    ts = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")
    processed_count = 0

    for p in all_players:
        print(f"Bager kopa: {p['name']}")
        stats = get_flashscore_stats(p.get('flash_id'))
        
        if stats:
            league = p.get('league', 'other').lower()
            club = p.get('club', 'unknown').lower()
            if league not in db: db[league] = {}
            if club not in db[league]: db[league][club] = {}
            
            db[league][club][p['name'].lower()] = {
                "stats": stats,
                "last_update": ts
            }
            processed_count += 1
            print(f"  -> Uspješno izvučeni kartoni i golovi za {p['name']}")

    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"Ukupno spremljeno: {processed_count} igrača.")

if __name__ == "__main__":
    main()
