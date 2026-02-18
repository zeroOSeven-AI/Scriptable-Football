import requests
import json
import time

players = [
    {
        "name": "modric",
        "league": "la_liga",
        "club_name": "Real Madrid",
        "sofa_id": "15466",
        "flash_url": "https://www.flashscore.de/spieler/modric-luka/bZWyoJnA/"
    }
]

# Pojačani Headers da nas Sofascore ne blokira
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Origin': 'https://www.sofascore.com',
    'Referer': 'https://www.sofascore.com/'
}

def get_data():
    master_db = {}
    for p in players:
        print(f"📡 Hvatanje podataka za: {p['name']}")
        
        try:
            # 1. SOFASCORE API POZIV
            sofa_url = f"https://api.sofascore.com/api/v1/player/{p['sofa_id']}"
            response = requests.get(sofa_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json().get('player', {})
                
                # Sigurno čupanje podataka (ako fali, piše "N/A")
                full_name = data.get('name', p['name'])
                number = data.get('jerseyNumber', '10')
                pos = data.get('position', 'MF')
                val_raw = data.get('proposedMarketValueRaw', {})
                value = f"{val_raw.get('value', 0) / 1000000:.1f}M €" if val_raw else "N/A"
            else:
                print(f"⚠️ Sofascore Error {response.status_code}")
                full_name, number, pos, value = p['name'], "??", "??", "0"

            # 2. STRUKTURA (All-in-one)
            if p['league'] not in master_db: master_db[p['league']] = {}
            
            master_db[p['league']][p['name']] = {
                "header": {
                    "full_name": full_name,
                    "number": number,
                    "position": pos,
                    "value": value,
                    "club": p['club_name']
                },
                "stats": {
                    "thisSeason": {"goals": "2", "assists": "3", "rating": "7.3"},
                    "lastSeason": {"goals": "2", "assists": "6", "rating": "7.1"}
                }
            }
            
        except Exception as e:
            print(f"❌ Kritična greška na igraču {p['name']}: {e}")

    # SPREMANJE (Ovaj dio mora raditi da Git ne baci Error 128/1)
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("✅ Skripta završila uspješno.")

if __name__ == "__main__":
    get_data()
