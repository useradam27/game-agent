import os, time, requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.environ["TWITCH_CLIENT_ID"]
CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]

PLATFORMS = {
    4: "NES",
    5: "Wii",
    6: "PC",
    7: "PS1",
    8: "PS2",
    9: "PS3",
    11: "XBOX",
    12: "X360",
    15: "C64",
    16: "Amiga",
    18: "NES",
    19: "SNES",
    20: "NDS",
    21: "NGC",
    22: "GBC",
    23: "DC",
    24: "GBA",
    29: "Genesis/MegaDrive",
    30: "Sega32",
    32: "Saturn",
    35: "Game Gear",
    37: "3DS",
    38: "PSP",
    41: "WiiU",
    42: "NGage",
    46: "Vita",
    47: "VC",
    48: "PS4",
    49: "XONE",
    72: "Ouya",
    78: "Sega CD",
    86: "turbografx16",
    87: "virtualboy",
    99: "famicom",
    130: "Switch",
    137: "New 3DS",
    162: "Oculus VR",
    163: "Steam VR",
    165: "PSVR",
    167: "PS5",
    169: "Series X|S",
    170: "Stadia",
    307: "G&W",
    381: "Playdate",
    390: "PSVR2",
    508: "Switch 2",
    510: "e-Reader"
}

_token = None
_last_call = 0.0


def get_token():
    """Exchange client credentials for an app access token."""
    global _token
    if _token:
        return _token
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    r.raise_for_status()
    _token = r.json()["access_token"]
    return _token


def igdb(endpoint, query):
    """POST an Apicalypse query to an IGDB endpoint. Throttled to stay under
    IGDB's 4 requests/second limit."""
    global _last_call

    # Simple throttle: never fire more than 3 requests per second.
    wait = 0.34 - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()

    r = requests.post(
        f"https://api.igdb.com/v4/{endpoint}",
        headers={
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {get_token()}",
        },
        data=query,
        timeout=30,
    )

    if r.status_code == 429:
        # Rate limited despite the throttle. Back off and retry once.
        time.sleep(2)
        return igdb(endpoint, query)

    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    games = igdb("games", "fields name, first_release_date; where platforms = (21); limit 10;")
    for g in games:
        print(g["name"])

    wanted = ["NES", "Super Nintendo", "Nintendo 64", "Game Boy",
          "Sega Mega Drive", "PlayStation", "Dreamcast"]

    rows = igdb("platforms", "fields id, name, abbreviation; limit 500;")
    for p in sorted(rows, key=lambda x: x["id"]):
        print(p["id"], "|", p.get("abbreviation", ""), "|", p["name"])

