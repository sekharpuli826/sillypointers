import sqlite3
import psycopg2

sqlite_conn = sqlite3.connect("cricket.db")
sqlite_cur = sqlite_conn.cursor()

pg_conn = psycopg2.connect(
    host="dpg-darem87avr4c73ec357g-a.oregon-postgres.render.com",
    database="sillypointers_db",
    user="sillypointers_db_user",
    password="DYEjDJFQsUK37i8WXLWcveYZzheCXV5D",
    port="5432"
)
pg_cur = pg_conn.cursor()

tables = [
    "tournament",
    "teams",
    "players",
    "matches",
    "innings",
    "balls",
    "points",
    "leaderboard"
]

for table in tables:
    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()

    for row in rows:
        placeholders = ",".join(["%s"] * len(row))
        pg_cur.execute(f"INSERT INTO {table} VALUES ({placeholders})", row)

pg_conn.commit()
pg_conn.close()
sqlite_conn.close()

print("Migration complete.")
