import requests
import json
import time

def fetch_football_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/"
    }
    
    # Ciljane lige
    leagues = {
        "HNL": 24, "Srbija": 247, "BiH": 550, "Turska": 52,
        "Nizozemska": 37, "Portugal": 238, "Engleska": 17,
        "Spanjolska": 8, "Italija": 11, "Njemacka": 37, "Francuska": 34
    }
    
    final_output = {}

    for name, t_id in leagues.items():
        try:
            # 1. Sezona
            s_url = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/seasons"
            s_res = requests.get(s_url, headers=headers).json()
            s_id = s_res['seasons'][0]['id']
            
            # 2. Tablica
            t_url = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/standings/total"
            t_res = requests.get(t_url, headers=headers).json()
            
            rows = []
            if 'standings' in t_res:
                # Uzimamo prvu tablicu koja ima podatke
                for std in t_res['standings']:
                    if 'rows' in std:
                        for r in std['rows'][:10]: # Top 10 timova
                            rows.append({
                                "pos": r['position'],
                                "name": r['team']['shortName'] or r['team']['name'],
                                "pts": r['points']
                            })
                        break
            
            if rows:
                final_output[name] = rows
                print(f"Uspješno: {name}")
            
            time.sleep(2) # Duža pauza da nas ne blokiraju
            
        except Exception as e:
            print(f"Preskačem {name}: Greška")

    # Zapisivanje - ako je final_output prazan, ne piši ništa (da ne obrišeš stare podatke)
    if final_output:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        print("Spremljeno u data.json!")
    else:
        print("Greška: Svi upiti su odbijeni.")

if __name__ == "__main__":
    fetch_football_data()
