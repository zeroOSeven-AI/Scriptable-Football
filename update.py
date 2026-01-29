import json

def fetch_data():
    # Potpuno fiksni podaci - bez interneta, bez API-ja
    test_data = {
        "name": "TESTNI TUNEL RADI",
        "matches": [
            {"home": "DINAMO", "homeId": 2400, "away": "HAJDUK", "awayId": 2410, "hScore": 3, "aScore": 0, "status": "finished", "time": "FT"}
        ],
        "table": [
            {"name": "DINAMO", "id": 2400, "pts": 100},
            {"name": "RIJEKA", "id": 2405, "pts": 80}
        ]
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    print("Testni podaci su upisani u data.json!")

if __name__ == "__main__":
    fetch_data()
