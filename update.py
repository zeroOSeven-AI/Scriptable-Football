import requests
import json
import time

def fetch_data():
    # Koristimo javni proxy tunel da sakrijemo GitHub IP adresu
    # Ovo će prevariti SofaScore da misli da zahtjev dolazi od običnog korisnika
    proxy_url = "https://api.allorigins.win/get?url="
    
    leagues = {
        "HNL": 24, "Srbija": 247, "BiH": 550, "Turska": 52,
        "Engleska": 17, "Spanjolska": 8, "Italija": 11, "Njemacka": 37
    }
    
    final_output = {}

    for name, t_id in leagues.items():
        try:
            # Prvo dohvaćamo sezonu
            s_api = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/seasons"
            res = requests.get(f"{proxy_url}{s_api}").json()
            
            # Allorigins pakira odgovor u 'contents' string, moramo ga pretvoriti u JSON
            s_data = json.loads(res['contents'])
            s_id = s_data['seasons'][0]['id']
            
            # Zatim dohvaćamo tablicu
            t_api = f"https://api.sofascore.com/api/v1/unique-tournament/{t_id}/season/{s_id}/standings/total"
            res_table = requests.get(f"{proxy_url}{t_api}").json()
            t_data = json.loads(res_table['contents'])
            
            rows = []
            if 'standings' in t_data:
                for std in t_data['standings']:
                    if 'rows' in std:
                        for r in std['rows'][:10]:
                            rows.append({
                                "pos": r['position'],
                                "name": r['team']['shortName'] or r['team']['name'],
                                "pts": r['points']
                            })
                        break
            
            if rows:
                final_output[name] = rows
                print(f"Uspjeh preko Proxy-ja: {name}")
            
            time.sleep(1) # Mala pauza
            
        except Exception as e:
            print(f"Greška na {name}: {e}")

    if final_output:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        print("Spremljeno!")
    else:
        print("I dalje blokirano. Morat ćemo koristiti Google Apps Script.")

if __name__ == "__main__":
    fetch_data()
