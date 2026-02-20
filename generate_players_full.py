import json

def generate():
    players = [
        {
            "name": "modric",
            "sofa_id": 15466,
            "flash_id": "modric-luka/bZWyoJnA",
            "league": "la_liga",
            "club": "real_madrid"
        },
        {
            "name": "leao",
            "sofa_id": 849074,
            "flash_id": "leao-rafael/AqOPWN5s",
            "league": "serie_a",
            "club": "ac_milan"
        },
        {
            "name": "bellingham",
            "sofa_id": 991011,
            "flash_id": "bellingham-jude/QNvlPm7s",
            "league": "la_liga",
            "club": "real_madrid"
        },
        {
            "name": "mbappe",
            "sofa_id": 166934,
            "flash_id": "mbappe-kylian/Wn6E2SED",
            "league": "la_liga",
            "club": "real_madrid"
        },
        {
            "name": "vinicius",
            "sofa_id": 872386,
            "flash_id": "vinicius-junior/CbwQ4Mws",
            "league": "la_liga",
            "club": "real_madrid"
        },
        {
            "name": "livaja",
            "sofa_id": 44431,
            "flash_id": "marko-livaja/8CyvzF4J",
            "league": "hnl",
            "club": "hajduk_split"
        }
    ]

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=2, ensure_ascii=False)
    print("SUCCESS: players.json generated with 6 players.")

if __name__ == "__main__":
    generate()
