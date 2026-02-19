import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import time

def scrape_player_data(url):
    # Simuliramo pravi Chrome browser na Windowsima
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200:
            print(f"Greška: Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # --- REGEX ZA ČUPANJE ---
        # Tržišna vrijednost (npr. €4.0m ili €180.0m)
        mv_match = re.search(r'Market value:\s*(€[\d.]+[mk])', text_data, re.IGNORECASE)
        market_value = mv_match.group(1) if mv_match else "TBA"

        # Istek ugovora
        ce_match = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        contract_until = ce_match.group(1) if ce_match else "TBA"

        # Zadnje ocjene (traži npr. 7.6 90')
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

    # Učitaj staru bazu da se ne obriše sve ako jedan scrape faila
    master_db = {}
    if os.path.exists('master_db.json'):
        with open('master_db.json', 'r', encoding='utf-8') as f:
            try:
                master_db = json.load(f)
            except:
                master_db = {}

    for player in players:
        p_name = player.get('name', '').lower()
        f_id = player.get('flash_id') # Čita tvoje novo polje!
        
        if f_id:
            url = f"https://www.flashscore.com/player/{f_id}/"
            print(f"🕵️ Bager kopa za: {p_name}...")
            
            new_data = scrape_player_data(url)
            if new_data:
                # Organiziramo JSON da ga Scriptable lako čita
                if p_name not in master_db:
                    master_db[p_name] = {}
                
                master_db[p_name]["flashscore"] = new_data
                print(f"✅ Nađeno: {new_data['market_value']} | Ocjene: {len(new_data['form_ratings'])}")
            
            time.sleep(2) # Pauza da nas ne blokiraju
        else:
            print(f"⚠️ Preskačem {p_name}, fali 'flash_id' u players.json")

    # Finalno spremanje u master_db.json
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("🚀 Master DB uspješno ažuriran!")

if __name__ == "__main__":
    main()
