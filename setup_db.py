import psycopg2

# Connect to your Render PostgreSQL database
conn = psycopg2.connect(
    host="dpg-darem87avr4c73ec357g-a.oregon-postgres.render.com",
    database="sillypointers_db",
    user="sillypointers_db_user",
    password="DYEjDJFQsUK37i8WXLWcveYZzheCXV5D",
    port="5432"
)
cur = conn.cursor()

# Tournament
cur.execute("""
CREATE TABLE IF NOT EXISTS tournament (
    id SERIAL PRIMARY KEY,
    name TEXT
);
""")

# Teams
cur.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    logo TEXT,
    created_at TEXT
);
""")

# Players
cur.execute("""
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name TEXT,
    role TEXT,
    team_id INTEGER,
    batting_position INTEGER,
    is_captain INTEGER DEFAULT 0,
    is_impact INTEGER DEFAULT 0,
    retired_hurt INTEGER DEFAULT 0,
    created_at TEXT
);
""")

# Matches
cur.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    team1_id INTEGER,
    team2_id INTEGER,
    overs INTEGER,
    venue TEXT,
    date TEXT,
    status TEXT,
    winner_id INTEGER
);
""")

# Innings (supports 1‑Declare)
cur.execute("""
CREATE TABLE IF NOT EXISTS innings (
    id SERIAL PRIMARY KEY,
    match_id INTEGER,
    batting_team_id INTEGER,
    bowling_team_id INTEGER,
    runs INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    overs REAL DEFAULT 0,
    declared INTEGER DEFAULT 0,
    nrr REAL DEFAULT 0
);
""")

# Ball-by-ball
cur.execute("""
CREATE TABLE IF NOT EXISTS balls (
    id SERIAL PRIMARY KEY,
    match_id INTEGER,
    innings_id INTEGER,
    over INTEGER,
    ball INTEGER,
    batsman_id INTEGER,
    bowler_id INTEGER,
    runs INTEGER,
    extra_type TEXT,
    is_wicket INTEGER,
    description TEXT,
    created_at TEXT
);
""")

# Points table
cur.execute("""
CREATE TABLE IF NOT EXISTS points (
    id SERIAL PRIMARY KEY,
    team_id INTEGER,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    nrr REAL DEFAULT 0,
    points INTEGER DEFAULT 0
);
""")

# Leaderboard
cur.execute("""
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    player_id INTEGER,
    runs INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    strike_rate REAL DEFAULT 0,
    economy REAL DEFAULT 0
);
""")

conn.commit()
conn.close()

print("PostgreSQL database initialized successfully.")
