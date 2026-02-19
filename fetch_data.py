import requests
import json
import re

# TOP LIGE
LEAGUES = {
    "la_liga": 8,
    "premier_league": 17,
    "serie_a": 23,
    "bundesliga": 35,
    "ligue_1": 34
}

SEASON_ID = 52186  # trenutna sezona (može se updateati)

BASE = "https://api.sofascore.com/api/v1/"

players = []

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")

for league_name, league_id in LEAGUES.items():
    print("League:", league_name)

    standings_url = f"{BASE}unique-tournament/{league_id}/season/{SEASON_ID}/standings/total"
    standings = requests.get(standings_url).json()

    teams = standings["standings"][0]["rows"]

    for row in teams:
        team = row["team"]
        team_id = team["id"]
        club_slug = slugify(team["name"])

        print("  Team:", team["name"])

        squad_url = f"{BASE}team/{team_id}/players"
        squad = requests.get(squad_url).json()

        for p in squad["players"]:
            player = p["player"]

            name_slug = slugify(player["name"])

            players.append({
                "name": name_slug,
                "sofa_id": player["id"],
                "flash_id": name_slug + "/",  # osnovni slug (može se kasnije precizirati)
                "league": league_name,
                "club": club_slug
            })

with open("players.json", "w", encoding="utf-8") as f:
    json.dump(players, f, indent=2, ensure_ascii=False)

print("Generated", len(players), "players")
