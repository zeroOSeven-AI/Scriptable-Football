import requests
import json

def fetch_data():
    # Premier League ID
    t_id = 17 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/"
    }

    try:
        # 1. Dohvat sezone
        s_res = requests.get(f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/seasons", headers=headers).json()
        s_id = s_res['seasons'][0]['id']
        
        # 2. Dohvat tablice
        t_res = requests.get(f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/standings/total", headers=headers).json()
        
        table_data = []
        if 'standings' in t_res:
            for row in t_res['standings'][0].get('rows', [])[:15]:
                table_data.append({
                    "name": row['team']['shortName'],
                    "id": row['team']['id'],
                    "pts": row['points']
                })

        # 3. Dohvat utakmica
        m_res = requests.get(f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/events/last/0", headers=headers).json()
        match_data = []
        if 'events' in m_res:
            for e in m_res['events'][-5:]:
                match_data.append({
                    "home": e['homeTeam']['shortName'],
                    "homeId": e['homeTeam']['id'],
                    "away": e['awayTeam']['shortName'],
                    "awayId": e['awayTeam']['id'],
                    "hScore": e.get('homeScore', {}).get('current', 0),
                    "aScore": e.get('awayScore', {}).get('current', 0),
                    "status": e['status']['type'],
                    "time": "FT"
                })

        final = {
            "name": "Premier League",
            "matches": match_data[::-1],
            "table": table_data
        }

        # Ako API ipak vrati prazno, nemoj prepisati Dinama (za svaki slučaj)
        if not table_data:
            print("API vratio prazno, zadržavam stare podatke.")
            return

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("Uspješno ažurirano s pravim podacima!")

    except Exception as e:
        print(f"Greška: {e}")

if __name__ == "__main__":
    fetch_data()
