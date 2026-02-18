import requests
import json
import time
import random

def get_stats(player_id):
    url = f"https://www.flashscore.com/player/{player_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Dodajemo random pauzu od 5-15 sekundi da nas ne provale
    time.sleep(random.randint(5, 15))
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    text = response.text
    # Ovdje koristimo sličnu logiku kao u JS bageru, ali za čisti HTML
    # (Za prototip možemo koristiti regex ili simple string split)
    return {"status": "ok", "raw_text_length": len(text)} # Demo placeholder

# Učitaj listu, prođi kroz njih, spremi master_db.json
# ... logika za spremanje ...
