import sqlite3, pathlib
from igdb import igdb, PLATFORMS

DB = pathlib.Path("games.db")


def init_db():
    conn = sqlite3.connect(DB)
    conn.executescript(pathlib.Path("loaders/schema.sql").read_text())
    return conn


def fetch_games(platform_ids):
    """Page through every game on the given platforms."""
    plat = ",".join(str(p) for p in platform_ids)
    fields = (
        "fields name, slug, first_release_date, rating, rating_count, summary, "
        "genres.id, genres.name, "
        "platforms.id, platforms.name, platforms.abbreviation, "
        "involved_companies.company.id, involved_companies.company.name, "
        "involved_companies.company.country, "
        "involved_companies.developer, involved_companies.publisher; "
    )
    out, offset = [], 0
    while True:
        q = f"{fields} where platforms = ({plat}); limit 500; offset {offset};"
        batch = igdb("games", q)
        if not batch:
            break
        out.extend(batch)
        offset += 500
        print(f"  fetched {len(out)} games...")
    return out


def load(conn, games):
    c = conn.cursor()
    for g in games:
        year = None
        if g.get("first_release_date"):
            # IGDB gives a unix timestamp; we only keep the year.
            import datetime
            year = datetime.datetime.utcfromtimestamp(
                g["first_release_date"]).year

        c.execute(
            "INSERT OR REPLACE INTO games "
            "(id, name, slug, first_release_year, rating, rating_count, summary) "
            "VALUES (?,?,?,?,?,?,?)",
            (g["id"], g["name"], g.get("slug"), year,
             g.get("rating"), g.get("rating_count"), g.get("summary")),
        )

        for p in g.get("platforms", []):
            c.execute("INSERT OR REPLACE INTO platforms VALUES (?,?,?)",
                      (p["id"], p["name"], p.get("abbreviation")))
            c.execute("INSERT OR REPLACE INTO game_platforms VALUES (?,?)",
                      (g["id"], p["id"]))

        for gen in g.get("genres", []):
            c.execute("INSERT OR REPLACE INTO genres VALUES (?,?)",
                      (gen["id"], gen["name"]))
            c.execute("INSERT OR REPLACE INTO game_genres VALUES (?,?)",
                      (g["id"], gen["id"]))

        for ic in g.get("involved_companies", []):
            co = ic.get("company")
            if not co:
                continue
            c.execute("INSERT OR REPLACE INTO companies VALUES (?,?,?)",
                      (co["id"], co["name"], co.get("country")))
            c.execute("INSERT OR REPLACE INTO game_companies VALUES (?,?,?,?)",
                      (g["id"], co["id"],
                       1 if ic.get("developer") else 0,
                       1 if ic.get("publisher") else 0))

    conn.commit()


def add_notes(conn):
    notes = [
        ("games", "rating", "IGDB user rating on a 0-100 scale. NULL for many "
         "obscure games. rating_count says how many users voted; a rating "
         "backed by 3 votes is not meaningful, so filter on rating_count "
         "when ranking."),
        ("games", "first_release_year", "Year only, as an integer. This is the "
         "earliest release on any platform, not the release year for a "
         "specific platform."),
        ("game_companies", "is_developer", "1 if this company developed the "
         "game. A game usually has both a developer and a publisher row, and "
         "sometimes the same company is both."),
        ("games", "summary", "Free text blurb. There is no review text and no "
         "sales data anywhere in this database."),
        ("people", "name", "Only directors are loaded, sourced from Wikidata. "
         "Coverage is partial: famous games have directors, obscure ones "
         "usually do not."),
    ]
    conn.executemany("INSERT INTO schema_notes VALUES (?,?,?)", notes)
    conn.commit()


if __name__ == "__main__":
    conn = init_db()
    games = fetch_games(list(PLATFORMS.keys()))
    print(f"Loading {len(games)} games...")
    load(conn, games)
    add_notes(conn)
    print("Done.")