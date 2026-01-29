import requests
import json

def fetch_data():
    # Pokušavamo se pretvarati da smo službena SofaScore Android aplikacija
    # Mobilni serveri (mobile.sofascore.com) su često blaži s blokadama
    url = "https://api.sofascore.com/api/v1/unique-tournament/24/season/61406/standings/total"
    
    headers = {
        "User-Agent": "SofaScore/Android/24.1.1",
        "Host": "api.sofascore.com",
        "Connection": "Keep-Alive"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if 'standings' in data:
            print("USPJEH! Mobilni server je otvoren.")
            # Ovdje ćemo dodati ostatak koda ako ovo prođe
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        else:
            print("I mobilni server nas odbija.")
            
    except Exception as e:
        print(f"Greška: {e}")

if __name__ == "__main__":
    fetch_data()
