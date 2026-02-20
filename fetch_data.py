import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import time

def scrape_flashscore(url):
    # Definiramo točna zaglavlja da izgledamo kao pravi korisnik
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    try:
        # Dodajemo headers u zahtjev
        response = scraper.get(url, headers=headers, timeout=25)
        
        if response.status_code != 200: 
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Flashscore nekad podatke drži u meta tagovima ako je JS blokiran
        # Pokušavamo izvući sav tekst za regex
        text = soup.get_text(separator=' ')

        mv = re.search(r'Market value:\s*(€[\d.]+[mk])', text, re.IGNORECASE)
        ce = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text)
        rt = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text)

        if not mv and not ce and not rt:
            # Ako klasični bager ne vidi, probaj tražiti u meta opisima (zadnja šansa)
            meta_desc = soup.find("meta", {"name": "description"})
            if meta_desc:
                text = meta_desc['content']
                mv = re.search(r'(€[\d.]+[mk])', text)

        if not mv and not ce and not rt:
            return None

        return {
            "market_value": mv.group(1) if mv else "TBA",
            "contract_until": ce.group(1) if ce else "TBA",
            "form_ratings": rt[:5] if rt else []
        }
    except Exception as e:
        print(f"      [!] Error: {str(e)}")
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
