import requests
import json
import time
import random
import re

# --- KONFIGURACIJA ---
PLAYERS_FILE = 'players.json'
DATABASE_FILE = 'master_db.json'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
}

def extract_stats(text, season_year):
    """Izvlači rating, golove, asiste i utakmice iz čistog teksta"""
    try:
        parts = text.split(season_year)
        if len(parts) < 2: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0"}
        
        chunk = parts[1][:300]
        nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
        idx = 0 if (nums and "." in nums[0]) else -1
        
        try:
            return {
                "rating": nums[idx] if idx >= 0 else "0.0",
                "matches": nums[idx+1] if len(nums) > idx+1 else "0",
                "goals": nums[idx+2] if len(nums) > idx+2 else "0",
                "assists": nums[idx+3] if len(nums) > idx+3 else "0"
            }
        except: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0"}
    except: return None

def run_bager():
    # 1. Učitaj popis igrača iz players.json
    try:
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            players_list = json.load(f)
    except Exception as e:
        print(f"❌ Greška: Ne mogu učitati {PLAYERS_FILE}. Provjeri zareze! Error: {e}")
        return

    # 2. Učitaj postojeću bazu (da ne brišemo stare ako bager zapne)
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            master_db = json.load(f)
    except:
        master_db = {}

    print(f"🚀 Pokrećem bager za {len(players_list)} igrača...")

    for p in players_list:
        name = p['name']
        liga = p['league']
        player_id = p['id'] # npr. "modric-luka/bZWyoJnA"
        
        print(f"⛏️  Kopam: {name} ({liga})...")
        
        try:
            url = f"https://www.flashscore.de/spieler/{player_id}/"
            time.sleep(random.randint(3, 7)) # Pauza da nas ne blokiraju
            
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"⚠️  Preskačem {name}, status: {r.status_code}")
                continue

            # Čistimo HTML za lakši regex
            clean_text = re.sub('<[^<]+?>', ' ', r.text)
            
            # Čupamo sezone
            this_s = extract_stats(clean_text, "2025/2026")
            last_s = extract_stats(clean_text, "2024/2025")

            # Spremanje u strukturu
            if liga not in master_db: master_db[liga] = {}
            
            master_db[liga][name] = {
                "header": {
                    "full_name": name.replace("-", " ").title(),
                    "club": p.get('club', 'Unknown Team'),
                    "position": "Player",
                    "value": "Check TM"
                },
                "stats": {
                    "thisSeason": this_s,
                    "lastSeason": last_s
                },
                "last_update": time.strftime("%H:%M:%S")
            }
            
            # Spremamo odmah nakon svakog igrača (sigurnost!)
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(master_db, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Greška kod {name}: {e}")

    print("✅ Bager završio. master_db.json je osvježen!")

if __name__ == "__main__":
    run_bager()
