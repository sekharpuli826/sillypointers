import sqlite3

DB = "cricket.db"


def get_conn():
    return sqlite3.connect(DB)


def add_team(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO teams (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def list_teams():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM teams ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows
