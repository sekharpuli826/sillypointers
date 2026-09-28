from db import get_conn

def start_innings(match_id, batting_team_id, bowling_team_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO innings (match_id, batting_team_id, bowling_team_id)
        VALUES (%s, %s, %s)
        RETURNING id;
    """, (match_id, batting_team_id, bowling_team_id))
    innings_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return innings_id


def get_current_over_ball(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(MAX(over), 0), COALESCE(MAX(ball), 0)
        FROM balls
        WHERE innings_id = %s;
    """, (innings_id,))
    over, ball = cur.fetchone()
    conn.close()
    return over, ball


def score_ball(match_id, innings_id, over, ball, batsman_id, bowler_id, runs, extra_type, is_wicket, description):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO balls (
            match_id, innings_id, over, ball,
            batsman_id, bowler_id, runs,
            extra_type, is_wicket, description, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
    """, (match_id, innings_id, over, ball, batsman_id, bowler_id, runs, extra_type, is_wicket, description))
    conn.commit()
    conn.close()


def declare_innings(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE innings SET declared = 1 WHERE id = %s;", (innings_id,))
    conn.commit()
    conn.close()


def retire_hurt(player_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE players SET retired_hurt = 1 WHERE id = %s;", (player_id,))
    conn.commit()
    conn.close()


def set_impact_player(player_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE players SET is_impact = 1 WHERE id = %s;", (player_id,))
    conn.commit()
    conn.close()
