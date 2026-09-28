import sqlite3

DB = "cricket.db"


def get_conn():
    return sqlite3.connect(DB)


def create_match(team1_id, team2_id, overs, venue, date, time):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO matches (team1_id, team2_id, overs, venue, date, time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (team1_id, team2_id, overs, venue, date, time))
    conn.commit()
    conn.close()


def list_matches():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id,
               t1.name AS team1,
               t2.name AS team2,
               m.overs,
               m.venue,
               m.date,
               m.time
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        ORDER BY m.date, m.time
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
