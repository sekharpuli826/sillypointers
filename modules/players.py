import sqlite3

DB = "cricket.db"


def get_conn():
    return sqlite3.connect(DB)


def add_player(name, role, team_id, bat_pos):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO players (name, role, team_id, bat_pos, status, is_impact)
        VALUES (?, ?, ?, ?, 'active', 0)
    """, (name, role, team_id, bat_pos))
    conn.commit()
    conn.close()


def list_players(team_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, role, bat_pos
        FROM players
        WHERE team_id = ?
        ORDER BY bat_pos
    """, (team_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
