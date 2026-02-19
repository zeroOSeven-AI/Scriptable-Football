import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import time

def scrape_full_data(url):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        txt = soup.get_text(separator=' ')

        # --- EKSTRAKCIJA SVEGA ---
        # 1. Novci (Market Value)
        mv = re.search(r'Market value:\s*(€[\d.]+[mk])', txt, re.IGNORECASE)
        # 2. Ugovor
        ce = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', txt)
        # 3. Ocjene (Forma)
        rt = re.findall(r'(\d\.\d)\s*\d{1,2}\'', txt)
        # 4. Pozicija i Godine (za svaki slučaj ako zatreba)
        age = re.search(r'Age:\s*(\d+)', txt)
        pos = re.search(r'([a-zA-Z]+)\s*\(AC Milan\)', txt) # Dinamički hvata poziciju uz klub

        return {
            "market_value": mv.group(1) if mv else "TBA",
            "contract": ce.group(1) if ce else "TBA",
            "ratings": rt[:5] if rt else [],
            "age": age.group(1) if age else "N/A",
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Greška pri čupanju: {e}")
        return None

def main():
    # Učitaj igrače
    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Učitaj staru bazu - KLJUČNO: NE BRISATI NIŠTA
    master_db = {}
    if os.path.exists('master_db.json'):
        with open('master_db.json', 'r', encoding='utf-8') as f:
            try: master_db = json.load(f)
            except: master_db = {}

    for p in players:
        p_name = p.get('name', '').lower()
        f_id = p.get('flash_id')
        
        if f_id:
            print(f"💰 Čupam lovu i podatke za: {p_name}...")
            scraped = scrape_full_data(f"https://www.flashscore.com/player/{f_id}/")
            
            if scraped:
                # Ako igrač već postoji u bazi, ne brišemo ga, nego DODAJEMO u njegovu granu
                if p_name not in master_db:
                    master_db[p_name] = {}
                
                # Kreiramo ili osvježavamo 'flashscore' granu
                master_db[p_name]["flashscore"] = scraped
                print(f"✅ Povučeno: {scraped['market_value']} i {len(scraped['ratings'])} ocjena.")
            
            time.sleep(3) # Polako da nas ne skuže

    # Spremi sve nazad
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("🚀 Sve je u bazi, novci osigurani.")

if __name__ == "__main__":
    main()
