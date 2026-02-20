import requests
import json
import time

LEAGUES = {
    "la_liga": "8",      # ID lige
    "serie_a": "23",
    "premier_league": "17"
}

OUTPUT = "players.json"


def get_json(url):
    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        print("HTTP error:", r.status_code)
        return None

    try:
        return r.json()
    except:
        print("❌ Nije JSON odgovor")
        print(r.text[:500])
        return None


players = []

for league, league_id in LEAGUES.items():
    print("League:", league)

    url = f"https://api.sofascore.com/api/v1/unique-tournament/{league_id}/season/52186/standings/total"

    data = get_json(url)

    if not data:
        continue

    # 🔒 zaštita od promjene strukture
    if "standings" not in data:
        print("❌ 'standings' key ne postoji")
        print("Keys:", data.keys())
        continue

    rows = data["standings"][0].get("rows", [])

    for team in rows:
        team_name = team["team"]["name"]

        players.append({
            "team": team_name,
            "league": league
        })

    time.sleep(1)


with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(players, f, indent=2, ensure_ascii=False)

print("✅ players.json napravljen")
