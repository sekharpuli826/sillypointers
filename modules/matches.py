from db import get_conn

def create_match(team1_id, team2_id, overs, venue, date):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO matches (team1_id, team2_id, overs, venue, date, status)
        VALUES (%s, %s, %s, %s, %s, 'scheduled')
        RETURNING id;
    """, (team1_id, team2_id, overs, venue, date))
    match_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return match_id


def list_matches():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, team1_id, team2_id, overs, venue, date, status, winner_id
        FROM matches
        ORDER BY id;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
