import streamlit as st
import pandas as pd
from src.attendance_logic import get_db_connection, calculate_hours_for_user, get_system_config

st.set_page_config(page_title="Leaderboard | Robotiator Files", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00251a; color: #e0f2f1; }
    h1 { color: #ffca28; text-align: center; font-size: 3rem; }
    .leaderboard-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #ffca28;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Robotiator Leaderboard")

config = get_system_config()
year = config.get('current_year')
season = config.get('current_season')

st.subheader(f"Current Deployment: {year} {season}")

conn = get_db_connection()
users = pd.read_sql_query("SELECT id, name, nickname FROM users", conn)
conn.close()

data = []
for _, user in users.iterrows():
    hours = calculate_hours_for_user(user['id'], year, season)
    display_name = user['nickname'] if user['nickname'] else user['name']
    data.append({"Personnel": display_name, "Hours": hours})

if data:
    df = pd.DataFrame(data).sort_values(by="Hours", ascending=False).reset_index(drop=True)
else:
    df = pd.DataFrame(columns=["Personnel", "Hours"])

if not df.empty:
    for idx, row in df.iterrows():
        medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🎖️"
        st.markdown(f"""
        <div class="leaderboard-card">
            <span style="font-size: 1.5rem;">{medal} #{idx+1} <b>{row['Personnel']}</b></span>
            <span style="float: right; font-size: 1.5rem; color: #ffca28;">{row['Hours']} Hours</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("The leaderboard is currently empty.")
