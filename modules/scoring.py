import sqlite3

DB = "cricket.db"


def get_conn():
    return sqlite3.connect(DB)


# -----------------------------
# INNINGS MANAGEMENT
# -----------------------------
def start_innings(match_id):
    conn = get_conn()
    cur = conn.cursor()

    # Create a new innings for the match
    cur.execute("""
        INSERT INTO innings (match_id, runs, wickets, overs, is_declared)
        VALUES (?, 0, 0, 0.0, 0)
    """, (match_id,))
    conn.commit()

    innings_id = cur.lastrowid
    conn.close()
    return innings_id


def declare_innings(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE innings SET is_declared = 1 WHERE id = ?", (innings_id,))
    conn.commit()
    conn.close()


def get_current_over_ball(innings_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT over, ball
        FROM balls
        WHERE innings_id = ?
        ORDER BY over DESC, ball DESC
        LIMIT 1
    """, (innings_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return row[0], row[1]
    else:
        return 0, 0  # start of innings


# -----------------------------
# BALL SCORING
# -----------------------------
def score_ball(match_id, innings_id, over, ball, batsman_id, bowler_id,
               runs, extra, wicket, description):
    conn = get_conn()
    cur = conn.cursor()

    # Insert ball
    cur.execute("""
        INSERT INTO balls (
            match_id, innings_id, over, ball,
            batsman_id, bowler_id, runs, extra, wicket, description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (match_id, innings_id, over, ball,
          batsman_id, bowler_id, runs, extra, wicket, description))

    # Update innings totals
    cur.execute("""
        UPDATE innings
        SET runs = runs + ?,
            wickets = wickets + ?
        WHERE id = ?
    """, (runs, wicket, innings_id))

    # Update overs (assuming 6 balls per over)
    cur.execute("""
        SELECT COUNT(*) FROM balls
        WHERE innings_id = ?
    """, (innings_id,))
    total_balls = cur.fetchone()[0]
    overs = total_balls // 6 + (total_balls % 6) / 10.0

    cur.execute("""
        UPDATE innings
        SET overs = ?
        WHERE id = ?
    """, (overs, innings_id))

    conn.commit()
    conn.close()


# -----------------------------
# RETIRE HURT / IMPACT PLAYER
# -----------------------------
def retire_hurt(player_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE players
        SET status = 'retire_hurt'
        WHERE id = ?
    """, (player_id,))
    conn.commit()
    conn.close()


def set_impact_player(player_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE players
        SET is_impact = 1
        WHERE id = ?
    """, (player_id,))
    conn.commit()
    conn.close()


# -----------------------------
# SCORECARD / STATS
# -----------------------------
def get_scorecard(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT runs, wickets, overs
        FROM innings
        WHERE id = ?
    """, (innings_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {"runs": 0, "wickets": 0, "overs": 0.0}

    return {
        "runs": row[0],
        "wickets": row[1],
        "overs": row[2]
    }


def get_batter_stats(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name,
               SUM(b.runs) AS runs,
               COUNT(b.id) AS balls,
               SUM(CASE WHEN b.wicket = 1 THEN 1 ELSE 0 END) AS outs
        FROM balls b
        JOIN players p ON b.batsman_id = p.id
        WHERE b.innings_id = ?
        GROUP BY p.name
        ORDER BY runs DESC
    """, (innings_id,))
    rows = cur.fetchall()
    conn.close()

    result = []
    for name, runs, balls, outs in rows:
        sr = (runs / balls * 100) if balls > 0 else 0
        result.append({
            "Batter": name,
            "Runs": runs,
            "Balls": balls,
            "Outs": outs,
            "Strike Rate": round(sr, 2)
        })
    return result


def get_bowler_stats(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name,
               SUM(b.runs) AS runs_conceded,
               COUNT(b.id) AS balls_bowled,
               SUM(CASE WHEN b.wicket = 1 THEN 1 ELSE 0 END) AS wickets
        FROM balls b
        JOIN players p ON b.bowler_id = p.id
        WHERE b.innings_id = ?
        GROUP BY p.name
        ORDER BY wickets DESC, runs_conceded ASC
    """, (innings_id,))
    rows = cur.fetchall()
    conn.close()

    result = []
    for name, runs_conceded, balls_bowled, wickets in rows:
        overs = balls_bowled // 6 + (balls_bowled % 6) / 10.0
        eco = (runs_conceded / overs) if overs > 0 else 0
        result.append({
            "Bowler": name,
            "Overs": overs,
            "Runs Conceded": runs_conceded,
            "Wickets": wickets,
            "Economy": round(eco, 2)
        })
    return result


def get_over_summary(innings_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT over,
               SUM(runs) AS runs_in_over,
               SUM(CASE WHEN wicket = 1 THEN 1 ELSE 0 END) AS wickets_in_over
        FROM balls
        WHERE innings_id = ?
        GROUP BY over
        ORDER BY over
    """, (innings_id,))
    rows = cur.fetchall()
    conn.close()

    result = []
    for over, runs_in_over, wickets_in_over in rows:
        result.append({
            "Over": over,
            "Runs": runs_in_over,
            "Wickets": wickets_in_over
        })
    return result


def get_live_score(match_id, innings_id):
    conn = get_conn()
    cur = conn.cursor()

    # Basic score
    cur.execute("""
        SELECT runs, wickets, overs
        FROM innings
        WHERE id = ?
    """, (innings_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {
            "runs": 0,
            "wickets": 0,
            "overs": 0.0,
            "current_over_detail": "",
            "partnership": "",
            "last_5_overs": []
        }

    runs, wickets, overs = row

    # Current over detail
    cur.execute("""
        SELECT over, ball, runs, extra, wicket
        FROM balls
        WHERE innings_id = ?
        ORDER BY over DESC, ball DESC
        LIMIT 6
    """, (innings_id,))
    balls = cur.fetchall()

    current_over_detail = ", ".join(
        [f"{b[0]}.{b[1]}: {b[2]} ({b[3]}){' W' if b[4] == 1 else ''}" for b in balls]
    )

    # Last 5 overs summary
    cur.execute("""
        SELECT over,
               SUM(runs) AS runs_in_over,
               SUM(CASE WHEN wicket = 1 THEN 1 ELSE 0 END) AS wickets_in_over
        FROM balls
        WHERE innings_id = ?
        GROUP BY over
        ORDER BY over DESC
        LIMIT 5
    """, (innings_id,))
    last_overs = cur.fetchall()

    last_5_overs = []
    for over_no, r, w in last_overs:
        last_5_overs.append({
            "Over": over_no,
            "Runs": r,
            "Wickets": w
        })

    # Simple partnership placeholder (could be enhanced)
    partnership = f"Partnership: {runs} runs (approx)"

    conn.close()

    return {
        "runs": runs,
        "wickets": wickets,
        "overs": overs,
        "current_over_detail": current_over_detail,
        "partnership": partnership,
        "last_5_overs": last_5_overs
    }
