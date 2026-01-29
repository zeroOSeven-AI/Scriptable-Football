import requests
import json
import random
import time

def fetch_data():
    # Koristimo Premier League (17) za test jer je najstabilnija
    t_id = 17 
    
    # Lista različitih User-Agenata da nas teže otkriju
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]

    headers = {
        "User-Agent": random.choice(ua_list),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/"
    }

    try:
        # 1. Prvo tražimo ID sezone
        s_res = requests.get(f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/seasons", headers=headers)
        s_id = s_res.json()['seasons'][0]['id']
        
        # Mali "sleep" da ne budemo prebrzi (sumnjivo serveru)
        time.sleep(1)

        # 2. Dohvat tablice
        t_url = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/standings/total"
        t_res = requests.get(t_url, headers=headers).json()
        
        table_data = []
        if 'standings' in t_res:
            for standing in t_res['standings']:
                if standing.get('type') == 'total':
                    for row in standing.get('rows', [])[:15]:
                        table_data.append({
                            "name": row['team']['shortName'],
                            "id": row['team']['id'],
                            "pts": row['points']
                        })
                    break

        # 3. Dohvat utakmica
        m_url = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/events/last/0"
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

        # Finalni JSON
        final = {
            "name": "Premier League",
            "matches": match_data[::-1],
            "table": table_data
        }

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("Bypass uspješan! Podaci spremljeni.")

    except Exception as e:
        print(f"Bypass nije uspio: {e}")

if __name__ == "__main__":
    fetch_data()
