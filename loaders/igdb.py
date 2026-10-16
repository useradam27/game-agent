import os, time, requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.environ["TWITCH_CLIENT_ID"]
CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]

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
    games = igdb("games", "fields name, first_release_date; where platforms = (19); limit 10;")
    for g in games:
        print(g["name"])