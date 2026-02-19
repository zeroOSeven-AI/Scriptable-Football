import cloudscraper
from bs4 import BeautifulSoup
import re, json
from datetime import datetime

BASE = "https://www.flashscore.com/player/"

with open("players.json", encoding="utf-8") as f:
    PLAYERS = json.load(f)

scraper = cloudscraper.create_scraper()

def scrape(url):
    r = scraper.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ")

    def find(pattern):
        m = re.search(pattern, text)
        return m.group(1) if m else None

    return {
        "market_value": find(r"Market value:\s*(€[\d.]+[mk])"),
        "contract_until": find(r"Contract expires:\s*(\d{2}\.\d{2}\.\d{4})"),
        "rating": (re.findall(r"(\d\.\d)\s*\d{1,2}'", text) or [None])[0]
    }

db = {}

for p in PLAYERS:
    try:
        url = BASE + p["flash_id"] + "/"
        print("Scraping:", p["name"])
        db[p["name"]] = scrape(url)
    except Exception as e:
        db[p["name"]] = {"error": str(e)}

with open("master_db.json", "w", encoding="utf-8") as f:
    json.dump(
        {"updated": datetime.utcnow().isoformat(), "data": db},
        f,
        indent=2,
        ensure_ascii=False
    )

print("MASTER DB SAVED")
