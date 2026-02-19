import cloudscraper
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

BASE = "https://www.flashscore.com/player/"

with open("players.json", "r", encoding="utf-8") as f:
    PLAYERS = json.load(f)

scraper = cloudscraper.create_scraper()

def scrape_player(player):
    url = BASE + player["flash_id"] + "/"

    try:
        r = scraper.get(url, timeout=30)
        if r.status_code != 200:
            return {"error": f"status {r.status_code}"}

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ")

        market = re.search(r"Market value:\s*(€[\d.]+[mk])", text)
        contract = re.search(r"Contract expires:\s*(\d{2}\.\d{2}\.\d{4})", text)
        ratings = re.findall(r"(\d\.\d)\s*\d{1,2}'", text)

        return {
            "market_value": market.group(1) if market else None,
            "contract_until": contract.group(1) if contract else None,
            "form_ratings": ratings[:5]
        }

    except Exception as e:
        return {"error": str(e)}


db = {}

for p in PLAYERS:
    print("Scraping:", p["name"])
    db[p["name"]] = scrape_player(p)

with open("master_db.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "updated": datetime.utcnow().isoformat(),
            "data": db
        },
        f,
        indent=2,
        ensure_ascii=False
    )

print("MASTER DB SAVED")
