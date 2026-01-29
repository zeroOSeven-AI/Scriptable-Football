import requests
import json

def fetch_data():
    # Koristimo ScoreBat besplatni API koji ne blokira GitHub
    url = "https://www.scorebat.com/video-api/v3/"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        match_data = []
        # ScoreBat daje listu trenutnih i nedavnih utakmica
        for match in data.get('response', [])[:10]:
            match_data.append({
                "home": match['title'].split(' - ')[0],
                "away": match['title'].split(' - ')[1],
                "league": match['competition'],
                "url": match['matchviewUrl'],
                "status": "finished"
            })

        # Budući da ScoreBat ne daje tablicu besplatno, 
        # ovdje ćemo držati tvoj HNL/Premier League backup dok ne nađemo novi izvor tablice
        final = {
            "name": "Live Football",
            "matches": match_data,
            "table": [
                {"name": "Dinamov Test", "id": 2400, "pts": 99},
                {"name": "Hajdukov Test", "id": 2410, "pts": 98}
            ]
        }

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("ScoreBat podaci spremljeni!")

    except Exception as e:
        print(f"Greška: {e}")

if __name__ == "__main__":
    fetch_data()
