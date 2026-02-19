import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os

def scrape_player_data(url):
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # Market Value
        mv_match = re.search(r'Market value:\s*(€[\d.]+[mk])', text_data)
        market_value = mv_match.group(1) if mv_match else "TBA"

        # Contract
        ce_match = re.search(r'Contract expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        contract_until = ce_match.group(1) if ce_match else "TBA"

        # Form Ratings
        ratings = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text_data)
        last_form = ratings[:5] if ratings else []

        return {
            "market_value": market_value,
            "contract_until": contract_until,
            "form_ratings": last_form
        }
    except:
        return None

def main():
    # 1. Učitaj listu igrača (prilagodi putanju ako treba)
    if not os.path.exists('players.json'):
        print("Greška: players.json ne postoji!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    # 2. Učitaj postojeći master_db ili napravi novi
    master_db = {}
    
    for player in players:
        name = player['name'].lower()
        # Flashscore URL mora biti u players.json ili ga ovdje definiraj
        # Pretpostavljam da koristiš 'flash_url' polje
        url = player.get('flash_url') 
        
        if url:
            print(f"Scraping {name}...")
            data = scrape_player_data(url)
            if data:
                # Ovdje čuvamo strukturu koju tvoj Scriptable očekuje
                master_db[name] = data
        
    # 3. Spremi sve u master_db.json
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("Master DB uspješno ažuriran.")

if __name__ == "__main__":
    main()
