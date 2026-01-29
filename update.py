import requests
import json

def fetch_data():
    # Pokušavamo ponovno s Premier Ligom (ID 17) jer je najsigurnija za test
    t_id = 17 
    
    # Ova zaglavlja su ključna - kopirana su iz stvarnog preglednika
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/",
        "Cache-Control": "max-age=0"
    }

    try:
        # Idemo direktno na API, ali s "prevarom" u zaglavlju
        # Koristimo i specifičan poddomenu api.sofascore.com
        s_res = requests.get(f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/seasons", headers=headers).json()
        s_id = s_res['seasons'][0]['id']
        
        t_url = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/standings/total"
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

        final = {
            "name": "Premier League",
            "matches": match_data[::-1],
            "table": table_data
        }

        # AKO JE I DALJE PRAZNO, pišemo testnu poruku da znamo da robot radi
        if not table_data:
            final["name"] = "SofaScore Block Active"

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print("Završen pokušaj ažuriranja.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_data()
