import requests
import json

def fetch_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    tournament_id = 7 # Champions League
    
    try:
        # 1. Pronađi ID trenutne sezone (Dynamic Search)
        s_res = requests.get(f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/seasons", headers=headers).json()
        current_season_id = s_res['seasons'][0]['id']
        print(f"Aktivna sezona ID: {current_season_id}")

        # 2. Dohvat tablice
        t_url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{current_season_id}/standings/total"
        t_res = requests.get(t_url, headers=headers).json()
        
        table_data = []
        # Tražimo 'rows' u standings-ima
        for standing in t_res.get('standings', []):
            if standing.get('type') == 'total':
                for row in standing.get('rows', [])[:20]:
                    table_data.append({
                        "name": row['team']['shortName'] or row['team']['name'],
                        "id": row['team']['id'],
                        "pts": row['points']
                    })
                break

        # 3. Dohvat zadnjih utakmica
        m_url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{current_season_id}/events/last/0"
        m_res = requests.get(m_url, headers=headers).json()
        
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

        # Finalna provjera - ako je tablica prazna, ne spremaj
        if not table_data:
            print("Tablica je i dalje prazna. Provjera strukture API-ja...")
            return

        final = {
            "name": "Champions League",
            "matches": match_data[::-1],
            "table": table_data
        }

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("Svemirski uspjeh! Podaci su u data.json")

    except Exception as e:
        print(f"Greška: {e}")

if __name__ == "__main__":
    fetch_data()
