import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os

def scrape_player_data(url):
    # Pokušavamo glumiti pravi browser još agresivnije
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200:
            print(f"Greška: Status {response.status_code} za URL")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # Tražimo Market Value (pokušavamo više varijanti regexa)
        mv_match = re.search(r'Market value:\s*(€[\d.]+[mk])', text_data, re.IGNORECASE)
        market_value = mv_match.group(1) if mv_match else "TBA"

        # Tražimo Contract
        ce_match = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        contract_until = ce_match.group(1) if ce_match else "TBA"

        # Tražimo ocjene
        ratings = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text_data)
        last_form = ratings[:5] if ratings else []

        return {
            "market_value": market_value,
            "contract_until": contract_until,
            "form_ratings": last_form
        }
    except Exception as e:
        print(f"Scrape error: {e}")
        return None

def main():
    if not os.path.exists('players.json'):
        print("Kritična greška: players.json nije pronađen!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Učitaj staru bazu da ne brišemo sve ako bager ne nađe ništa
    master_db = {}
    if os.path.exists('master_db.json'):
        with open('master_db.json', 'r', encoding='utf-8') as f:
            try:
                master_db = json.load(f)
            except:
                master_db = {}

    for player in players:
        # PAŽNJA: Provjeri zove li se u tvom players.json polje 'name' i 'flash_url'
        p_name = player.get('name', 'unknown').lower()
        url = player.get('flash_url') # Provjeri ovaj naziv u svom JSON-u!
        
        if url:
            print(f"Obrađujem: {p_name}")
            new_data = scrape_player_data(url)
            if new_data:
                # Spajamo stare stats s novim podacima da ne izgubimo povijest
                if p_name not in master_db:
                    master_db[p_name] = {"stats": {}}
                
                master_db[p_name]["flashscore"] = new_data
                print(f"Uspješno spremljeno za {p_name}: {new_data['market_value']}")
        else:
            print(f"Preskačem {p_name}, nema flash_url polja.")
        
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
