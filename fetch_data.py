import requests
import json
import time
import random
import re

# HEADERS - da izgledamo kao pravi browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    try:
        # RANDOM PAUZA: Da Flashscore ne skuži bot (između 5 i 15 sekundi)
        time.sleep(random.randint(5, 15))
        
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200: return None
        
        text = re.sub('<[^<]+?>', ' ', r.text)
        
        def parse_season(year):
            parts = text.split(year)
            if len(parts) < 2: return {"rating":"0.0", "goals":"0", "assists":"0"}
            chunk = parts[1][:300]
            nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
            idx = 0 if (nums and "." in nums[0]) else -1
            try:
                return {
                    "rating": nums[idx] if idx >= 0 else "0.0",
                    "matches": nums[idx+1],
                    "goals": nums[idx+2],
                    "assists": nums[idx+3]
                }
            except: return {"rating":"0.0", "goals":"0", "assists":"0"}

        return {
            "thisSeason": parse_season("2025/2026"),
            "lastSeason": parse_season("2024/2025")
        }
    except: return None

def main():
    # 1. Učitaj listu igrača
    with open('players.json', 'r') as f:
        players = json.load(f)
    
    # 2. Učitaj postojeću bazu (da ne brišemo stare ako bager stane)
    try:
        with open('master_db.json', 'r') as f:
            master_db = json.load(f)
    except:
        master_db = {}

    # 3. Kreni u rudnik
    for p in players:
        print(f"⛏️ Kopam za: {p['name']}...")
        stats = get_stats(p['id'])
        
        if stats:
            league = p['league']
            if league not in master_db: master_db[league] = {}
            master_db[league][p['name']] = {
                "header": {"full_name": p['name'].capitalize(), "value": "Check TM"},
                "stats": stats
            }
            # Spremi nakon svakog igrača (za svaki slučaj)
            with open('master_db.json', 'w', encoding='utf-8') as f:
                json.dump(master_db, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
