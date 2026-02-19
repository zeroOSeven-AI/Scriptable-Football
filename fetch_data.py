import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import time

def scrape_player_data(url):
    # Pokušavamo 3 puta ako ne uspije iz prve
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    for attempt in range(3):
        try:
            response = scraper.get(url, timeout=15)
            # Čekamo 2 sekunde da budemo sigurni
            time.sleep(2) 
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Uzimamo sav tekst ali i specifične klase ako postoje
            text_data = soup.get_text(separator=' ')

            # --- PRECIZNIJI REGEX ---
            
            # Traži € broj i slovo m ili k (npr €4.0m ili €500k)
            market_val_match = re.search(r'Market value:\s*(€[\d.]+[mk]?)', text_data, re.IGNORECASE)
            market_value = market_val_match.group(1) if market_val_match else "TBA"

            # Traži datum u bilo kojem formatu koji liči na ugovor
            contract_match = re.search(r'expires:\s*(\d{2}\.\d{2}\.\d{4})', text_data)
            contract_until = contract_match.group(1) if contract_match else "TBA"

            # Traži ocjene - Flashscore ih često drži u formatu "broj.broj" blizu minuta
            ratings = re.findall(r'(\d\.\d)\s*(?=\d{1,2}\')', text_data)
            last_form = ratings[:5] if ratings else []

            # Ako smo barem nešto našli, prekidamo petlju
            if market_value != "TBA" or last_form:
                return {
                    "market_value": market_value,
                    "contract_until": contract_until,
                    "form_ratings": last_form
                }
            
            time.sleep(3) # Pauza prije novog pokušaja
        except Exception as e:
            print(f"Pokušaj {attempt+1} propao: {e}")
            
    return {"market_value": "TBA", "contract_until": "TBA", "form_ratings": []}

# Test za Modrića
player_url = "https://www.flashscore.com/player/modric-luka/bZWyoJnA/"
data = scrape_player_data(player_url)
print(json.dumps(data, indent=2))
