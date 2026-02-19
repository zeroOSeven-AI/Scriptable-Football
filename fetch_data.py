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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    try:
        # Nasumična odgoda (kao tvoj Timer u Scriptableu)
        time.sleep(random.uniform(7, 12))
        
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"⚠️ Status {response.status_code} za {player_id}")
            return None
        
        # Čistimo HTML ali ostavljamo tekst za ekstrakciju
        text = re.sub('<[^<]+?>', ' ', response.text)
        
        # --- EKSTRAKCIJA PODATAKA (Logika iz tvog Scriptable-a) ---
        
        # Ime (uzimamo prvi red teksta)
        name_search = text.split('\n')[0].strip()
        
        # Klub (Tražimo 'Current club' ili slično)
        club = "Nepoznato"
        club_match = re.search(r"(?:Current club|Team):\s*([A-Za-z0-9\s]+)", text)
        if club_match:
            club = club_match.group(1).strip()
            
        # Tržišna vrijednost (Regex iz tvog koda)
        market_value = "N/A"
        value_match = re.search(r"Market value:\s*(€[0-9.]+[m|k])", text, re.I)
        if value_match:
            market_value = value_match.group(1)
            
        # Datum rođenja i zemlja
        birthday = "N/A"
        birth_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", text)
        if birth_match: birthday = birth_match.group(1)
        
        country = "N/A"
        country_match = re.search(r"Nationality:\s*([A-Za-z\s]+)", text)
        if country_match: country = country_match.group(1).strip()

        # Funkcija za statistiku (sezona)
        def extract_season(year):
            if year not in text: 
                return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
            try:
                parts = text.split(year)
                chunk = parts[1][:400]
                nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
                if not nums: return {"rating": "0.0", "matches": "0", "goals": "0", "assists": "0", "yellow": "0", "red": "0"}
                
                has_rating = "." in nums[0]
                i = 0 if has_rating else -1
                
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
            "header": {
                "full_name": name_search,
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
        print(f"❌ Greška kod obrade: {e}")
        return None

def main():
    # 1. Učitaj igrače
    if not os.path.exists(PLAYERS_FILE):
        print("❌ Nema players.json!")
        return
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        all_players = json.load(f)

    # 2. Provjeri index (gdje smo stali)
    start_idx = 0
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            try:
                start_idx = int(f.read().strip())
            except: start_idx = 0
    
    if start_idx >= len(all_players): start_idx = 0

    # 3. Odredi batch
    end_idx = start_idx + BATCH_SIZE
    current_batch = all_players[start_idx:end_idx]
    
    # 4. Učitaj bazu (Sigurna verzija protiv JSONDecodeErrora)
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    db = json.loads(content)
        except:
            print("⚠️ Baza oštećena, krećem ispočetka.")
            db = {}

    # Naše vrijeme (Hrvatska)
    hr_vrijeme = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m. %H:%M")

    print(f"🚀 Batch: {start_idx} do {min(end_idx, len(all_players))}. Igrača: {len(all_players)}")

    for p in current_batch:
        name_key = p['name'].lower()
        liga = p.get('league', 'ostalo').lower()
        klub = p.get('club', 'nepoznato').lower()
        
        print(f"⛏️  Kopam: {name_key}...")
        data = get_player_stats(p['id'])
        
        if data:
            # Troslojna struktura: Liga -> Klub -> Igrač
            if liga not in db: db[liga] = {}
            if klub not in db[liga]: db[liga][klub] = {}
            
            db[liga][klub][name_key] = {
                "info": data['header'],
                "stats": data['stats'],
                "last_update": hr_vrijeme
            }
            print(f"✅ Spremljeno: {name_key}")

    # 5. Spremi bazu i index
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    with open(INDEX_FILE, 'w') as f:
        f.write(str(end_idx if end_idx < len(all_players) else 0))

    print(f"✅ Batch gotov. Idući put krecem od indexa: {end_idx}")

if __name__ == "__main__":
    main()
