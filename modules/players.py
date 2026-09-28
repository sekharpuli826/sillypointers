from db import get_conn

def add_player(name, role, team_id, batting_position):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO players (name, role, team_id, batting_position, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id;
    """, (name, role, team_id, batting_position))
    player_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return player_id


def list_players(team_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, role, batting_position, is_captain, is_impact, retired_hurt
        FROM players
        WHERE team_id = %s
        ORDER BY batting_position;
    """, (team_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
