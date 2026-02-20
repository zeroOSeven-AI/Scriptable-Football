import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import time

def scrape_flashscore(url):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')

        # Tražimo podatke
        mv = re.search(r'Market value:\s*(€[\d.]+[mk])', text, re.IGNORECASE)
        ce = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text)
        rt = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text)

        # AKO NIJE NAŠAO NIŠTA, VRATI NONE (da ne pregazimo stare podatke s TBA)
        if not mv and not ce and not rt:
            return None

        return {
            "market_value": mv.group(1) if mv else "TBA",
            "contract_until": ce.group(1) if ce else "TBA",
            "form_ratings": rt[:5] if rt else []
        }
    except:
        return None

def main():
    db_path = 'master_db.json'
    
    # 1. UČITAJ POSTOJEĆU BAZU (Sve što imaš od prije)
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            try:
                master_db = json.load(f)
            except:
                master_db = {}
    else:
        master_db = {}

    # 2. UČITAJ POPIS IGRAČA
    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    for p in players:
        p_name = p.get('name', '').lower()
        f_id = p.get('flash_id')
        
        if f_id:
            print(f"Checking for updates: {p_name}...")
            new_info = scrape_flashscore(f"https://www.flashscore.com/player/{f_id}/")
            
            if new_info:
                # AKO IGRAČ VEĆ POSTOJI, SAMO DOPUNI (MERGE)
                if p_name not in master_db:
                    master_db[p_name] = {}
                
                # Ako unutar igrača već postoji 'flashscore' grana, dopuni je
                if "flashscore" not in master_db[p_name]:
                    master_db[p_name]["flashscore"] = {}
                
                # Update - zamjenjuje samo ono što je novo, ostalo ostavlja
                master_db[p_name]["flashscore"].update(new_info)
                master_db[p_name]["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"   [+] Updated: {new_info['market_value']}")
            else:
                print(f"   [!] No new data found for {p_name}, keeping old data.")

    # 3. SPREMI SVE NAZAD
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("Process finished safely.")

if __name__ == "__main__":
    main()
