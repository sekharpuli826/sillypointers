from db import get_conn

def update_nrr(innings_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT runs, wickets, overs
        FROM innings
        WHERE id = %s;
    """, (innings_id,))
    runs, wickets, overs = cur.fetchone()

    if overs == 0:
        nrr = 0
    else:
        nrr = runs / overs

    cur.execute("""
        UPDATE innings
        SET nrr = %s
        WHERE id = %s;
    """, (nrr, innings_id))

    conn.commit()
    conn.close()
