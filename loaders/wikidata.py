import sqlite3, requests

ENDPOINT = "https://query.wikidata.org/sparql"

# P5794 and P9043 are both IGDB identifier properties on Wikidata; different
# items carry different ones. We ask for both and join on whichever is present.
QUERY = """
SELECT ?game ?igdbSlug ?igdbNum ?directorLabel WHERE {
  ?game wdt:P31/wdt:P279* wd:Q7889 .
  ?game wdt:P57 ?director .
  OPTIONAL { ?game wdt:P5794 ?igdbSlug . }
  OPTIONAL { ?game wdt:P9043 ?igdbNum . }
  FILTER (BOUND(?igdbSlug) || BOUND(?igdbNum))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

HEADERS = {
    # Wikidata requires a descriptive User-Agent identifying your app and a
    # contact. Requests without one are refused.
    "User-Agent": "game-agent/0.1 (https://github.com/useradam27/game-agent)",
    "Accept": "application/sparql-results+json",
}


def fetch_directors():
    r = requests.get(ENDPOINT, params={"query": QUERY, "format": "json"},
                     headers=HEADERS, timeout=120)
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def load(conn, rows):
    c = conn.cursor()
    matched = 0
    for row in rows:
        name = row["directorLabel"]["value"]
        qid  = row["game"]["value"].rsplit("/", 1)[-1]

        # Try the numeric IGDB id first, then fall back to the slug.
        game_id = None
        if "igdbNum" in row:
            hit = c.execute("SELECT id FROM games WHERE id = ?",
                            (int(row["igdbNum"]["value"]),)).fetchone()
            game_id = hit[0] if hit else None
        if game_id is None and "igdbSlug" in row:
            hit = c.execute("SELECT id FROM games WHERE slug = ?",
                            (row["igdbSlug"]["value"],)).fetchone()
            game_id = hit[0] if hit else None

        if game_id is None:
            continue   # game not in our platform slice

        c.execute("INSERT OR IGNORE INTO people (wikidata_qid, name) VALUES (?,?)",
                  (qid, name))
        pid = c.execute("SELECT id FROM people WHERE wikidata_qid = ?",
                        (qid,)).fetchone()[0]
        c.execute("INSERT OR IGNORE INTO game_directors VALUES (?,?)",
                  (game_id, pid))
        matched += 1

    conn.commit()
    print(f"Matched {matched} director credits to games in our slice.")


if __name__ == "__main__":
    conn = sqlite3.connect("games.db")
    load(conn, fetch_directors())