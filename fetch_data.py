import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import time

def scrape_player_details(url):
    # Initializing scraper to bypass Cloudflare
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200:
            print(f"Error: Status {response.status_code} for URL")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_text = soup.get_text(separator=' ')

        # --- DATA EXTRACTION (English Keys) ---
        
        # Market Value Extraction
        mv_match = re.search(r'Market value:\s*(€[\d.]+[mk])', raw_text, re.IGNORECASE)
        market_value = mv_match.group(1) if mv_match else "TBA"

        # Contract Expiration Extraction
        ce_match = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', raw_text)
        contract_until = ce_match.group(1) if ce_match else "TBA"

        # Recent Ratings Extraction
        ratings = re.findall(r'(\d\.\d)\s*\d{1,2}\'', raw_text)
        form_ratings = ratings[:5] if ratings else []

        return {
            "market_value": market_value,
            "contract_until": contract_until,
            "form_ratings": form_ratings,
            "last_sync": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Scrape process failed: {e}")
        return None

def main():
    # Load player configuration
    if not os.path.exists('players.json'):
        print("Critical Error: players.json not found!")
        return

    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Load existing database to prevent data loss (Merge Strategy)
    master_db = {}
    if os.path.exists('master_db.json'):
        with open('master_db.json', 'r', encoding='utf-8') as f:
            try:
                master_db = json.load(f)
            except:
                master_db = {}

    for player in players:
        player_name = player.get('name', 'unknown').lower()
        flash_id = player.get('flash_id')
        
        if flash_id:
            print(f"Fetching data for: {player_name}...")
            url = f"https://www.flashscore.com/player/{flash_id}/"
            new_data = scrape_player_details(url)
            
            if new_data:
                # Ensure the player exists in master_db
                if player_name not in master_db:
                    master_db[player_name] = {}
                
                # Update only the flashscore branch
                master_db[player_name]["flashscore"] = new_data
                print(f"Success: {player_name} updated. Value: {new_data['market_value']}")
            
            time.sleep(3) # Anti-bot delay
        else:
            print(f"Skipping {player_name}: No flash_id provided.")

    # Save merged data
    with open('master_db.json', 'w', encoding='utf-8') as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)
    print("Database sync completed successfully.")

if __name__ == "__main__":
    main()
