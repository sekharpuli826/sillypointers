from db import get_conn

def add_team(name, logo=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO teams (name, logo, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id;
    """, (name, logo))
    team_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return team_id


def list_teams():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, logo, created_at FROM teams ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return rows
