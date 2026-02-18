import requests
import re
import json
import time

# 1. TVOJA LISTA IGRAČA S LINKOVIMA
# Kad budeš dodavao nove, samo kopiraš ovaj blok
players = [
    {
        "name": "modric",
        "club": "Real Madrid", # Ili AC Milan kako si stavio
        "league": "la_liga",
        "links": {
            "flash": "https://www.flashscore.de/spieler/modric-luka/bZWyoJnA/",
            "sofa": "https://api.sofascore.com/api/v1/player/15466", # API je bolji od linka!
            "tm": "https://www.transfermarkt.de/luka-modric/profil/spieler/27992"
        }
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_data():
    master_db = {}

    for p in players:
        print(f"🚀 VYRA AGGREGATOR: Sakupljam sve za {p['name']}...")
        
        # --- IZVOR 1: SOFASCORE (API) ---
        # Ovo čupa: Vrijednost, Broj, Poziciju, Godine
        sofa_res = requests.get(p['links']['sofa'], headers=headers).json()
        player_info = sofa_res.get('player', {})
        
        # --- IZVOR 2: FLASHSCORE (SCRAPER) ---
        # Ovo čupa: Golove i asiste (koristimo onaj tvoj "snajper")
        flash_res = requests.get(p['links']['flash'], headers=headers).text
        # (Ovdje ide ona naša regex logika za sezone...)
        
        # --- SPAJANJE U JEDAN KOŠ ---
        if p['league'] not in master_db: master_db[p['league']] = {}
        
        master_db[p['league']][p['name']] = {
            "header": {
                "full_name": player_info.get('name', p['name']),
                "number": player_info.get('jerseyNumber', '??'),
                "position": player_info.get('position', '??'),
                "value": player_info.get('proposedMarketValueRaw', {}).get('value', '0')
            },
            "stats": {
                "thisSeason": {"goals": "2", "assists": "3", "rating": "7.3"}, # Primjer
                "lastSeason": {"goals": "2", "assists": "6", "rating": "7.1"}
            }
        }
        
        time.sleep(2) # Da nas ne blokiraju

    # SPREMANJE
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_data()
