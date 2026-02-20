import cloudscraper
from bs4 import BeautifulSoup
import re
import json

def scrape_player_data(url):
    # Inicijalizacija scrapera koji zaobilazi Cloudflare zaštitu
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url)
        if response.status_code != 200:
            return {"error": f"Status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text(separator=' ')

        # --- REGEX OPERACIJA (Čupanje iz onog što si mi poslao) ---
        
        # 1. Market Value (traži simbol € i broj nakon kojeg slijedi m ili k)
        market_val_match = re.search(r'Market value:\s*(€[\d.]+[mk])', text_data)
        market_value = market_val_match.group(1) if market_val_match else "TBA"

        # 2. Contract Expires (traži datum u formatu DD.MM.YYYY)
        contract_match = re.search(r'Contract expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
        contract_until = contract_match.group(1) if contract_match else "TBA"

        # 3. Zadnje ocjene (traži brojeve poput 7.0, 7.6 koji stoje uz minute 90')
        ratings = re.findall(r'(\d\.\d)\s*\d{1,2}\'', text_data)
        last_form = ratings[:5] if ratings else []

        return {
            "market_value": market_value,
            "contract_until": contract_until,
            "form_ratings": last_form
        }

    except Exception as e:
        return {"error": str(e)}

# Primjer korištenja za Modrića
player_url = "https://www.flashscore.com/player/modric-luka/bZWyoJnA/"
data = scrape_player_data(player_url)

# Printamo rezultat da vidiš kako ga bager sprema
print(json.dumps(data, indent=2))

# Ovdje bi išao tvoj kod koji ovaj 'data' sprema u master_db.json na GitHub
