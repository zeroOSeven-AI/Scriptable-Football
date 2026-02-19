import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import time

def scrape_player_data(url):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        # Flashscore nekad treba mrvicu duže da "pusti" botove
        response = scraper.get(url, timeout=20)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # Tražimo Market Value
        mv_match = re.search(r'Market value:\s*(€[\d.]+[mk])', text_data, re.IGNORECASE)
        market_value = mv_match.group(1) if mv_match else "TBA"

        # Tražimo Contract
        ce_match = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        contract_until = ce_match.group(1) if ce_match else "TBA"

        # Tražimo ocjene (npr. 7.6 90')
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
        print("Greška: players.json ne postoji!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Učitaj staru bazu da ne gubimo podatke
    master_db = {}
    if os.path.exists('master_db.json'):
        with open('master_db.json', 'r', encoding='utf-8') as f:
            try: master_db = json.load(f)
            except: master_db = {}

    # MAPA ZA URL-ove (Dodaj ovdje ID-ove s Flashscorea za ostale igrače)
    # Format: "ime_iz_jsona": "id_s_flashscorea"
    flash_ids = {
        "modric": "modric-luka/bZWyoJnA",
        "leao": "rafael-leao/88998G9a",
        "bellingham": "bellingham-jude/S688v999",
        "mbappe": "mbappe-kylian/8888v999",
        "vinicius": "vinicius-junior/8888v999",
        "livaja": "livaja-marko/8888v999"
    }

    for player in players:
        p_name = player.get('name', '').lower()
        
        # Ako imamo ID u mapi, sastavljamo URL
        if p_name in flash_ids:
            url = f"https://www.flashscore.com/player/{flash_ids[p_name]}/"
            print(f"Kopam za: {p_name}")
            
            new_data = scrape_player_data(url)
            if new_data:
                if p_name not in master_db:
                    master_db[p_name] = {}
                
                # Spremamo pod ključ 'flashscore'
                master_db[p_name]["flashscore"] = new_data
                print(f"Nađeno: {new_data['market_value']}")
            
            time.sleep(2) # Mala pauza da nas ne blokiraju
        else:
            print(f"Preskačem {p_name}, nije definiran Flashscore ID u Pythonu.")

    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
