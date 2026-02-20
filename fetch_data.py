import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os

def scrape_player_details(url):
    # 'delay' scraper koji zaobilazi Cloudflare zaštitu
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # --- REGEX ZA NOVCE I STATSE ---
        mv = re.search(r'Market value:\s*(€[\d.]+[mk]?)', text_data, re.IGNORECASE)
        ce = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        rt = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text_data)

        return {
            "market_value": mv.group(1) if mv else "TBA",
            "contract_until": ce.group(1) if ce else "TBA",
            "form_ratings": rt[:5] if rt else []
        }
    except:
        return None

def main():
    # 1. Učitaj tvoj generirani players.json
    if not os.path.exists('players.json'):
        print("Error: players.json not found!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    # 2. Učitaj master_db (da ne brišemo stare Sofa podatke)
    db_path = 'master_db.json'
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            master_db = json.load(f)
    else:
        master_db = {}

    # 3. Kreni u čupanje podataka
    for p in players:
        p_name = p.get('name', '').lower()
        f_id = p.get('flash_id') # Koristi tvoj ID iz JSON-a
        
        if f_id:
            print(f"Syncing data for: {p_name}...")
            url = f"https://www.flashscore.com/player/{f_id}/"
            new_data = scrape_player_details(url)
            
            if new_data:
                if p_name not in master_db:
                    master_db[p_name] = {}
                # Dodajemo Flashscore granu unutar igrača
                master_db[p_name]["flashscore"] = new_data
                print(f"Success: {p_name} -> {new_data['market_value']}")

    # 4. Spremi sve
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
