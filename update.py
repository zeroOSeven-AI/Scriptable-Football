import requests
import json

def get_sofa_data():
    # Primjer za Champions League (Tournament ID: 7, Season: 64152)
    url = "https://api.sofascore.com/api/v1/unique-tournament/7/season/64152/standings/total"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Ovdje robot skuplja podatke umjesto tebe
    response = requests.get(url, headers=headers).json()
    rows = response['standings'][0]['rows']
    
    table = []
    for r in rows[:10]:
        table.append({
            "name": r['team']['shortName'],
            "id": r['team']['id'],
            "pts": r['points']
        })
    
    # Spremamo u data.json
    final_data = {
        "name": "Champions League",
        "matches": [], # Ovdje se mogu dodati i live utakmice
        "table": table
    }
    
    with open('data.json', 'w') as f:
        json.dump(final_data, f, indent=2)

if __name__ == "__main__":
    get_sofa_data()
