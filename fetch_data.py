import requests
import json
import re
import time

# Lista igrača koje pratiš
players_to_track = [
    {
        "name": "modric",
        "league": "serie_a",
        "club": "AC Milan",
        "flash_url": "https://www.flashscore.de/spieler/modric-luka/bZWyoJnA/"
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_stats(text, season_year):
    try:
        # Tražimo dio teksta nakon sezone
        parts = text.split(season_year)
        if len(parts) < 2: return None
        
        chunk = parts[1][:300]
        # Hvata ocjenu (npr. 7.3) i brojeve iza (nastupi, golovi, asisti, žuti)
        nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
        
        # Ako prvi broj nije ocjena (nema tačku), prilagođavamo index
        idx = 0 if (nums and "." in nums[0]) else -1
        
        return {
            "rating": nums[idx] if idx >= 0 else "0.0",
            "matches": nums[idx+1] if len(nums) > idx+1 else "0",
            "goals": nums[idx+2] if len(nums) > idx+2 else "0",
            "assists": nums[idx+3] if len(nums) > idx+3 else "0",
            "yellow": nums[idx+4] if len(nums) > idx+4 else "0"
        }
    except:
        return None

def run_bager():
    master_db = {}
    
    for p in players_to_track:
        print(f"🕵️ Bager otvara rudnik za: {p['name']}")
        try:
            r = requests.get(p['flash_url'], headers=headers, timeout=15)
            if r.status_code != 200: continue
            
            clean_text = re.sub('<[^<]+?>', ' ', r.text) # Čistimo HTML tagove
            
            this_season = extract_stats(clean_text, "2025/2026")
            last_season = extract_stats(clean_text, "2024/2025")
            
            if p['league'] not in master_db: master_db[p['league']] = {}
            
            master_db[p['league']][p['name']] = {
                "header": {
                    "full_name": "Luka Modrić",
                    "club": p['club'],
                    "value": "€4.0m",
                    "position": "MC/DM"
                },
                "stats": {
                    "thisSeason": this_season if this_season else {"rating":"0.0","goals":"0","assists":"0"},
                    "lastSeason": last_season if last_season else {"rating":"0.0","goals":"0","assists":"0"}
                },
                "last_update": time.strftime("%H:%M:%S")
            }
        except Exception as e:
            print(f"❌ Greška kod {p['name']}: {e}")

    # KLJUČNI DIO: Spremanje u file koji GitHub gura dalje
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    
    print("✅ SVE JE SPREMLJENO U master_db.json")

if __name__ == "__main__":
    run_bager()
