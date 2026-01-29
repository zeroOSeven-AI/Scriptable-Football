import requests
import json

def fetch_data():
    # ID za Ligu Prvaka (Tournament 7, Season 64152)
    # Možeš dodati i druge lige ovdje kasnije
    url_table = "https://api.sofascore.com/api/v1/unique-tournament/7/season/64152/standings/total"
    url_matches = "https://api.sofascore.com/api/v1/unique-tournament/7/season/64152/events/last/0"
    
    headers = {"User-Agent": "Mozilla/5.0"}

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
        "name": "Champions League",
        "matches": match_data[::-1],
        "table": table_data
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_data()
