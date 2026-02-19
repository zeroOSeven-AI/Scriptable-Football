import requests
import json
import time
import random
import re
import os
from datetime import datetime, timedelta

# POSTAVKE BATCHA
BATCH_SIZE = 50 
INDEX_FILE = 'last_index.txt'

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    
    try:
        time.sleep(random.uniform(5, 10))
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200: return None
        
        # Čistimo HTML ali ostavljamo više teksta za header podatke
        full_text = re.sub('<[^<]+?>', ' ', r.text)
        
        # --- EKSTRAKCIJA HEADER PODATAKA (Rođenje, Zemlja) ---
        birthday = "Unknown"
        country = "Unknown"
        
        # Tražimo datum (npr. 24.06.1987)
        birth_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", full_text)
        if birth_match: birthday = birth_match.group(1)
        
        # Nacionalnost se obično nalazi blizu imena ili u specifičnom nizu
        # Ovo je pojednostavljena verzija; Flashscore često koristi ikone, 
        # ali u tekstu ostane naziv države pored profila.
        country_match = re.search(r"Nationality:\s*([A-Za-z\s]+)", full_text)
        if country_match: country = country_match.group(1).strip()

        def extract_season(year):
            if year not in full_text: return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0"}
            parts = full_text.split(year)
            chunk = parts[1][:400]
            nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
            i = 0 if (nums and "." in nums[0]) else -1
            try:
                return {
                    "rating": nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1] if len(nums) > i+1 else "0",
                    "goals": nums[i+2] if len(nums) > i+2 else "0",
                    "assists": nums[i+3] if len(nums) > i+3 else "0"
                }
            except: return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0"}

        return {
            "info": {"birthday": birthday, "country": country},
            "stats": {"thisSeason": extract_season("2025/2026"), "lastSeason": extract_season("2024/2025")}
        }
    except: return None

def main():
    # 1. Učitaj sve igrače
    if not os.path.exists('players.json'): return
    with open('players.json', 'r', encoding='utf-8') as f:
        all_players = json.load(f)

    # 2. Provjeri gdje smo stali
    start_idx = 0
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            start_idx = int(f.read().strip())
    
    if start_idx >= len(all_players): start_idx = 0

    # 3. Odredi batch (npr. od 50 do 100)
    end_idx = start_idx + BATCH_SIZE
    current_batch = all_players[start_idx:end_idx]
    
       # 4. Učitaj postojeću bazu (SIGURNA VERZIJA)
    db = {}
    if os.path.exists('master_db.json'):
        try:
            with open('master_db.json', 'r', encoding='utf-8') as f:
                sadrzaj = f.read().strip()
                if sadrzaj: # Ako file nije skroz prazan
                    db = json.loads(sadrzaj)
        except Exception as e:
            print(f"⚠️ Baza je bila pokvarena ({e}), krećem ispočetka.")
            db = {}

    hr_vrijeme = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")

    print(f"🚀 Batch: {start_idx} do {min(end_idx, len(all_players))}. Ukupno: {len(all_players)}")

    for p in current_batch:
        name = p['name'].lower()
        liga = p.get('league', 'ostalo').lower()
        klub = p.get('club', 'nepoznato').lower()
        
        print(f"⛏️  Kopam: {name}...")
        data = get_player_stats(p['id'])
        
        if data:
            if liga not in db: db[liga] = {}
            if klub not in db[liga]: db[liga][klub] = {}
            
            db[liga][klub][name] = {
                "header": {
                    "full_name": p['name'],
                    "birthday": data['info']['birthday'],
                    "country": data['info']['country']
                },
                "stats": data['stats'],
                "last_update": hr_vrijeme
            }

    # 5. Spremi bazu i novi index
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    with open(INDEX_FILE, 'w') as f:
        f.write(str(end_idx if end_idx < len(all_players) else 0))

    print(f"✅ Batch gotov. Idući put krećem od: {end_idx}")

if __name__ == "__main__":
    main()
