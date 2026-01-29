import requests
import json

def fetch_data():
    # ID za Ligu Prvaka 25/26 (Tournament: 7, Season: 67123)
    # Napomena: ID sezone se mijenja, ovo je trenutno najsvježiji
    url_table = "https://api.sofascore.com/api/v1/unique-tournament/7/season/67123/standings/total"
    url_matches = "https://api.sofascore.com/api/v1/unique-tournament/7/season/67123/events/last/0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Dohvat tablice
        t_res = requests.get(url_table, headers=headers).json()
        table_data = []
        if 'standings' in t_res:
            for row in t_res['standings'][0]['rows'][:20]:
                table_data.append({
                    "name": row['team']['shortName'] or row['team']['name'],
                    "id": row['team']['id'],
                    "pts": row['points']
                })

        # Dohvat utakmica
        m_res = requests.get(url_matches, headers=headers).json()
        match_data = []
        if 'events' in m_res:
            # Uzimamo zadnjih 5 završenih ili live utakmica
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
        
        # Ako je sve prazno, nemoj prepisati data.json starim podacima
        if not table_data:
            print("Greška: Podaci su prazni, provjeri ID sezone!")
            return

        final = {
            "name": "Champions League",
            "matches": match_data[::-1],
            "table": table_data
        }

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("Uspješno ažurirano!")

    except Exception as e:
        print(f"Došlo je do greške: {e}")

if __name__ == "__main__":
    fetch_data()
