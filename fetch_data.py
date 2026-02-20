import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import sys

def scrape_player_details(url):
    # 'delay' scraper with fake browser headers
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200:
            print(f"      [!] URL Error: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # --- REGEX EXTRACTION ---
        mv = re.search(r'Market value:\s*(€[\d.]+[mk]?)', text_data, re.IGNORECASE)
        ce = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        rt = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text_data)

        return {
            "market_value": mv.group(1) if mv else "TBA",
            "contract_until": ce.group(1) if ce else "TBA",
            "form_ratings": rt[:5] if rt else []
        }
    except Exception as e:
        print(f"      [!] Scraping failed: {e}")
        return None

def main():
    # 1. Check for players.json safely
    if not os.path.exists('players.json'):
        print("CRITICAL: players.json is missing!")
        sys.exit(1)

    try:
        with open('players.json', 'r', encoding='utf-8') as f:
            players = json.load(f)
    except Exception as e:
        print(f"CRITICAL: Could not read players.json: {e}")
        sys.exit(1)

    # 2. Load master_db safely
    master_db = {}
    if os.path.exists('master_db.json'):
        try:
            with open('master_db.json', 'r', encoding='utf-8') as f:
                master_db = json.load(f)
        except:
            print("Notice: master_db.json is corrupted or empty, starting fresh.")
            master_db = {}

    # 3. Process players
    print(f"Starting sync for {len(players)} players...")
    for p in players:
        p_name = p.get('name', 'unknown').lower()
        f_id = p.get('flash_id')
        
        if f_id:
            print(f" -> Syncing: {p_name}")
            url = f"https://www.flashscore.com/player/{f_id}/"
            new_data = scrape_player_details(url)
            
            if new_data:
                if p_name not in master_db:
                    master_db[p_name] = {}
                master_db[p_name]["flashscore"] = new_data
                print(f"    [+] {new_data['market_value']}")
        else:
            print(f" -> Skipping {p_name}: No flash_id")

    # 4. Save final result
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("SUCCESS: master_db.json updated.")

if __name__ == "__main__":
    main()
