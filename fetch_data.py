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
        # Povećana pauza da nas ne blokiraju
        time.sleep(random.randint(5, 10))
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200: 
            print(f"⚠️ Server vratio status {response.status_code}")
            return None
        
        text = re.sub('<[^<]+?>', ' ', response.text)
        
        def extract_season(year):
            if year not in text:
                return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}
            
            parts = text.split(year)
            chunk = parts[1][:300]
            nums = re.findall(r"(\d+\.\d+|\b\d+\b)", chunk)
            
            if not nums:
                return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}
                
            i = 0 if "." in nums[0] else -1
            
            try:
                return {
                    "rating":  nums[i] if i >= 0 else "0.0",
                    "matches": nums[i+1] if len(nums) > i+1 else "0",
                    "goals":   nums[i+2] if len(nums) > i+2 else "0",
                    "assists": nums[i+3] if len(nums) > i+3 else "0",
                    "yellow":  nums[i+4] if len(nums) > i+4 else "0"
                }
            except:
                return {"rating":"0.0", "matches":"0", "goals":"0", "assists":"0", "yellow":"0"}

        return {
            "thisSeason": extract_season("2025/2026"),
            "lastSeason": extract_season("2024/2025")
        }
    except Exception as e:
        print(f"❌ Greška pri dohvaćanju: {e}")
        return None

def main():
    if not os.path.exists('players.json'):
        print("❌ Nema players.json")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players_list = json.load(f)

    db = {}
    print(f"🚀 Krećem na {len(players_list)} igrača...")

    for p in players_list:
        name = p['name'].lower()
        print(f"⛏️  Kopam: {name}...")
        
        try:
            stats = get_player_stats(p['id'])
            if stats:
                db[name] = {
                    "header": {
                        "full_name": p['name'],
                        "club": "Football Club",
                        "value": "Check TM"
                    },
                    "stats": stats,
                    "last_update": time.strftime("%H:%M")
                }
                print(f"✅ Uspješno: {name}")
            else:
                print(f"⚠️ Preskačem: {name} (nema podataka)")
        except Exception as e:
            print(f"❌ Ozbiljna greška kod {name}: {e}")
            continue # Idi na idućeg igrača, nemoj ugasiti bager!

    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Gotovo! Spremljeno {len(db)} igrača.")

if __name__ == "__main__":
    main()
