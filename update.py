import requests
import json
import random

def fetch_data():
    # Koristimo javni proxy servis da sakrijemo GitHub IP
    # Ovaj URL služi kao tunel koji SofaScore ne blokira
    proxy_url = "https://api.allorigins.win/raw?url="
    target_tournament = 17 # Premier League
    
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}

    try:
        # 1. Dohvat Sezone preko tunela
        s_url = f"{proxy_url}https://api.sofascore.com/api/v1/unique-tournament/{target_tournament}/seasons"
        s_res = requests.get(s_url, headers=headers).json()
        s_id = s_res['seasons'][0]['id']
        
        # 2. Dohvat Tablice preko tunela
        t_url = f"{proxy_url}https://api.sofascore.com/api/v1/unique-tournament/{target_tournament}/season/{s_id}/standings/total"
        t_res = requests.get(t_url, headers=headers).json()
        
        table_data = []
        if 'standings' in t_res:
            rows = t_res['standings'][0].get('rows', [])
            for row in rows[:15]:
                table_data.append({
                    "name": row['team']['shortName'],
                    "id": row['team']['id'],
                    "pts": row['points']
                })

        # 3. Dohvat Utakmica preko tunela
        m_url = f"{proxy_url}https://api.sofascore.com/api/v1/unique-tournament/{target_tournament}/season/{s_id}/events/last/0"
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

        final = {
            "name": "Premier League",
            "matches": match_data[::-1],
            "table": table_data
        }

        # Ako je i ovo prazno, ispiši grešku u logove
        if not table_data:
            print("Tunnel returned empty data. SofaScore is onto us.")
            return

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("TUNNEL SUCCESS! data.json is updated.")

    except Exception as e:
        print(f"Tunnel error: {e}")

if __name__ == "__main__":
    fetch_data()
