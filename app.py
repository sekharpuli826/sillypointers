import streamlit as st
import sqlite3
import pandas as pd
import time

from modules.teams import add_team, list_teams
from modules.players import add_player, list_players
from modules.matches import create_match, list_matches
from modules.scoring import (
    start_innings, score_ball, declare_innings,
    retire_hurt, set_impact_player, get_current_over_ball,
    get_scorecard, get_bowler_stats, get_batter_stats,
    get_over_summary, get_live_score
)

DB = "cricket.db"

# -----------------------------
# Sidebar Navigation
# -----------------------------
page = st.sidebar.selectbox(
    "Menu",
    [
        "Tournament Setup",
        "Teams",
        "Players",
        "Matches",
        "Ball Update",
        "Scorecard",
        "Live Match"
    ]
)

st.title("🏏 Silly Pointers Cricket Tournament Manager")


# ============================================================
# 1️⃣ TOURNAMENT SETUP
# ============================================================
if page == "Tournament Setup":
    st.header("Tournament Setup")

    t_name = st.text_input("Tournament Name")
    if st.button("Save Tournament Name"):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("DELETE FROM tournament")
        cur.execute("INSERT INTO tournament (name) VALUES (?)", (t_name,))
        conn.commit()
        conn.close()
        st.success(f"Tournament named: {t_name}")


# ============================================================
# 2️⃣ TEAMS
# ============================================================
elif page == "Teams":
    st.header("Teams")

    team_name = st.text_input("Add Team")
    if st.button("Create Team"):
        add_team(team_name)
        st.success(f"Team added: {team_name}")

    teams = list_teams()
    st.write("### Current Teams")
    st.table(teams)


# ============================================================
# 3️⃣ PLAYERS
# ============================================================
elif page == "Players":
    st.header("Players")

    teams = list_teams()
    team_ids = [t[0] for t in teams]
    team_select = st.selectbox("Select Team", team_ids)

    player_name = st.text_input("Player Name")
    role = st.selectbox("Role", ["batsman", "bowler", "all-rounder", "keeper"])
    bat_pos = st.number_input("Batting Position", min_value=1, max_value=11)

    if st.button("Add Player"):
        add_player(player_name, role, team_select, bat_pos)
        st.success(f"Player added: {player_name}")

    st.write("### Players in Team")
    st.table(list_players(team_select))


# ============================================================
# 4️⃣ MATCHES
# ============================================================
elif page == "Matches":
    st.header("Matches")

    teams = list_teams()
    team_ids = [t[0] for t in teams]

    team1 = st.selectbox("Team 1", team_ids)
    team2 = st.selectbox("Team 2", team_ids)
    overs = st.number_input("Overs", min_value=1, max_value=50)
    venue = st.text_input("Venue")
    date = st.date_input("Match Date")
    match_time = st.time_input("Match Time")


    if st.button("Create Match"):
       create_match(team1, team2, overs, venue, str(date), str(match_time))
    st.success("Match created!")


    st.write("### All Matches")
    st.table(list_matches())


# ============================================================
# 5️⃣ BALL UPDATE (SCORING)
# ============================================================
elif page == "Ball Update":
    st.header("Ball-by-Ball Scoring")

    match_id = st.number_input("Match ID", min_value=1)
    innings_id = st.number_input("Innings ID", min_value=1)

    if st.button("Start Innings"):
        start_innings(match_id)
        st.success("Innings started!")

    over, ball = get_current_over_ball(innings_id)
    st.write(f"Current Over: {over}, Ball: {ball}")

    batsman = st.number_input("Batsman ID", min_value=1)
    bowler = st.number_input("Bowler ID", min_value=1)
    runs = st.number_input("Runs", min_value=0)
    extra = st.selectbox("Extra", ["none", "wide", "no-ball", "bye", "leg-bye"])
    wicket = st.selectbox("Wicket?", [0, 1])
    desc = st.text_input("Description")

    if st.button("Score Ball"):
        score_ball(match_id, innings_id, over, ball + 1, batsman, bowler, runs, extra, wicket, desc)
        st.success("Ball scored!")

    if st.button("Declare Innings"):
        declare_innings(innings_id)
        st.success("Innings declared!")

    retire_id = st.number_input("Retire Hurt Player ID", min_value=1)
    if st.button("Retire Hurt"):
        retire_hurt(retire_id)
        st.success("Player marked as Retire Hurt")

    impact_id = st.number_input("Impact Player ID", min_value=1)
    if st.button("Set Impact Player"):
        set_impact_player(impact_id)
        st.success("Impact player set!")


# ============================================================
# 6️⃣ SCORECARD (FULL)
# ============================================================
elif page == "Scorecard":
    st.header("📊 Full Scorecard")

    innings_id = st.number_input("Innings ID", min_value=1)

    st.subheader("Batter Stats")
    batter_df = pd.DataFrame(get_batter_stats(innings_id))
    st.table(batter_df)

    st.subheader("Bowler Stats")
    bowler_df = pd.DataFrame(get_bowler_stats(innings_id))
    st.table(bowler_df)

    st.subheader("Over-by-Over Summary")
    over_df = pd.DataFrame(get_over_summary(innings_id))
    st.table(over_df)

    st.subheader("Total Score")
    score = get_scorecard(innings_id)
    st.write(f"Runs: {score['runs']} | Wickets: {score['wickets']} | Overs: {score['overs']}")

    rr = score["runs"] / (score["overs"] if score["overs"] > 0 else 1)
    st.write(f"Run Rate: {rr:.2f}")


# ============================================================
# 7️⃣ LIVE MATCH DASHBOARD (AUTO REFRESH)
# ============================================================
elif page == "Live Match":
    st.header("🔴 Live Match Dashboard")

    match_id = st.number_input("Match ID", min_value=1)
    innings_id = st.number_input("Innings ID", min_value=1)

    placeholder = st.empty()

    while st.checkbox("Auto Refresh Live Score"):
        with placeholder.container():
            score = get_live_score(match_id, innings_id)

            st.subheader("Score")
            st.write(f"{score['runs']}/{score['wickets']} in {score['overs']} overs")

            st.subheader("Current Over")
            st.write(score["current_over_detail"])

            st.subheader("Partnership")
            st.write(score["partnership"])

            st.subheader("Last 5 Overs")
            st.table(pd.DataFrame(score["last_5_overs"]))

        time.sleep(3)
