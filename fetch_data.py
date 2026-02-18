import requests
import json
import time
import random
import re
import os

def get_player_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Tvoja provjerena pauza
        time.sleep(random.randint(3, 7))
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
        
        text = re.sub('<[^<]+?>', ' ', response.text)
        
        def extract_season(year):
            parts = text.split(year)
            if len(parts) < 2: return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}
            
            chunk = parts[1][:300]
            nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
            i = 0 if (nums and "." in nums[0]) else -1
            
            try:
                return {
                    "rating":  nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1],
                    "goals":   nums[i+2],
                    "assists": nums[i+3],
                    "yellow":  nums[i+4]
                }
            except:
                return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}

        return {
            "thisSeason": extract_season("2025/2026"),
            "lastSeason": extract_season("2024/2025")
        }
    except Exception as e:
        print(f"Greška: {e}")
        return None

# --- AUTOMATSKO ČITANJE LISTE ---
def main():
    # Učitaj igrače iz tvog players.json filea
    if not os.path.exists('players.json'):
        print("❌ Greška: Ne postoji players.json!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players_to_fetch = json.load(f)

    db = {}
    print(f"🚀 Pokrećem bager za {len(players_to_fetch)} igrača...")

    for p in players_to_fetch:
        # Koristimo podatke iz JSON-a
        p_id = p['id']
        name = p['name'].lower()
        # Ako u players.json nemaš ligu ili klub, stavi default da ne pukne
        liga = p.get('league', 'ostalo').lower()
        club = p.get('club', 'nepoznato').lower()
        
        print(f"⛏️  Bager kopa: {name}...")
        stats = get_player_stats(p_id)
        
        if stats:
            # Kreiramo strukturu točno kako ti želiš
            if liga not in db: db[liga] = {}
            if club not in db: db[liga][club] = {}
            
            db[liga][club][name] = stats

    # Spremanje u master_db.json
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print("✅ master_db.json je uspješno generiran.")

if __name__ == "__main__":
    main()
