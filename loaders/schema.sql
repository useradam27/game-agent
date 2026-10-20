CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT,
    first_release_year INTEGER,
    rating REAL,
    rating_count INTEGER,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country INTEGER
);

CREATE TABLE IF NOT EXISTS game_companies (
    game_id INTEGER,
    company_id INTEGER,
    is_developer INTEGER,
    is_publisher INTEGER,
    PRIMARY KEY (game_id, company_id, is_developer, is_publisher)
);

CREATE TABLE IF NOT EXISTS platforms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    abbreviation TEXT
);

CREATE TABLE IF NOT EXISTS game_platforms (
    game_id INTEGER,
    platform_id INTEGER,
    PRIMARY KEY (game_id, platform_id)
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_genres (
    game_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (game_id, genre_id)
);

CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wikidata_qid TEXT UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_directors (
    game_id INTEGER,
    person_id INTEGER,
    PRIMARY KEY (game_id, person_id)
);

CREATE TABLE IF NOT EXISTS schema_notes (
    table_name TEXT,
    column_name TEXT,
    note TEXT
);

CREATE INDEX IF NOT EXISTS idx_games_name ON games(name);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);