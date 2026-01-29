import requests
import json
import time

def fetch_football_data():
    # Standardna zaglavlja da izgledamo kao pravi preglednik
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/"
    }
    
    # Popis liga s njihovim SofaScore ID-ovima
    leagues = {
        "HNL": 24,
        "Srbija": 247,
        "BiH": 550,
        "Turska": 52,
        "Nizozemska": 37,
        "Portugal": 238,
        "Engleska": 17,
        "Spanjolska": 8,
        "Italija": 11,
        "Njemacka": 37,
        "Francuska": 34,
        "Liga Prvaka": 7
    }
    
    all_leagues_results = {}

    print(f"Pokrećem ažuriranje: pronađeno {len(leagues)} liga.")

    for name, tournament_id in leagues.items():
        try:
            # 1. Dohvat ID-a trenutne sezone
            season_url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/seasons"
            season_res = requests.get(season_url, headers=headers).json()
            current_season_id = season_res['seasons'][0]['id']
            
            # 2. Dohvat tablice za tu sezonu
            table_url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{current_season_id}/standings/total"
            table_res = requests.get(table_url, headers=headers).json()
            
            league_table = []
            if 'standings' in table_res:
                for standing in table_res['standings']:
                    if standing['type'] == 'total':
                        for row in standing.get('rows', []):
                            league_table.append({
                                "pos": row['position'],
                                "name": row['team']['shortName'] or row['team']['name'],
                                "id": row['team']['id'],
                                "pts": row['points']
                            })
                        break
            
            all_leagues_results[name] = league_table
            print(f"Uspješno dohvaćeno: {name}")
            
            # Kratka pauza da nas ne blokiraju
            time.sleep(1.2)

        except Exception as e:
            print(f"Greška kod lige {name}: {str(e)}")

    # Spremanje svih podataka u data.json
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(all_leagues_results, f, indent=2, ensure_ascii=False)
        print("USPJEH: data.json je ažuriran sa svim ligama.")
    except Exception as e:
        print(f"Greška pri zapisivanju datoteke: {e}")

if __name__ == "__main__":
    fetch_football_data()
