import requests
import json
import re
import time
from bs4 import BeautifulSoup

LEAGUES = {
    "la_liga": 8,
    "premier_league": 17,
    "serie_a": 23,
    "bundesliga": 35,
    "ligue_1": 34
}

SEASON_ID = 52186
BASE = "https://api.sofascore.com/api/v1/"
FLASH_SEARCH = "https://www.flashscore.com/search/?q="

players = []


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def find_flash_id(player_name):
    """Vrati flashscore slug tipa: modric-luka/bZWyoJnA"""
    try:
        url = FLASH_SEARCH + player_name.replace(" ", "%20")
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")

        link = soup.select_one("a[href*='/player/']")
        if not link:
            return ""

        href = link["href"]  # /player/modric-luka/bZWyoJnA/
        parts = href.split("/player/")[-1].strip("/")

        return parts

    except Exception:
        return ""


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
            flash_id = find_flash_id(player["name"])

            players.append({
                "name": name_slug,
                "sofa_id": player["id"],
                "flash_id": flash_id,
                "league": league_name,
                "club": club_slug
            })

            print("    ✔", player["name"], "→", flash_id)

            time.sleep(0.5)  # anti-block


with open("players.json", "w", encoding="utf-8") as f:
    json.dump(players, f, indent=2, ensure_ascii=False)

print("\n✅ GOTOVO:", len(players), "igrača spremljeno u players.json")
