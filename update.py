import requests
import json
import time

def fetch_football_data():
    # Standard headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/"
    }
    
    # Dictionary of leagues with their SofaScore Unique Tournament IDs
    leagues = {
        "HNL": 24,
        "Serbia": 247,
        "BiH": 550,
        "Turkey": 52,
        "Netherlands": 37,
        "Portugal": 238,
        "England": 17,
        "Spain": 8,
        "Italy": 11,
        "Germany": 37,
        "France": 34,
        "Champions League": 7
    }
    
    all_leagues_results = {}

    print(f"Starting update: {len(leagues)} leagues found.")

    for name, tournament_id in leagues.items():
        try:
            # 1. Fetch the current season ID for the tournament
            season_url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/seasons"
            season_res = requests.get(season_url, headers=headers).json()
            current_season_id = season_res['seasons'][0]['id']
            
            # 2. Fetch the standings/table for that season
            table_url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{current_season_id}/standings/total"
            table_res = requests.get(table_url, headers=headers).json()
            
            league_table = []
            if 'standings' in table_res:
                # We look for the 'total' standing type
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
            print(f"Successfully fetched: {name}")
            
            # Anti-spam delay
            time.sleep(1.2)

        except Exception as e:
            print(f"Error skipping {name}: {str(e)}")

    # Save all gathered data into data.json
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(all_leagues_results, f, indent=2, ensure_ascii=False)
        print("SUCCESS: data.json has been updated with all leagues.")
    except Exception as e:
        print(f"File writing error: {e}")

if __name__ == "__main__":
    fetch_football_data()
