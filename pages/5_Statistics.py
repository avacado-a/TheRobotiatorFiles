import streamlit as st
import pandas as pd
import plotly.express as px
from src.attendance_logic import get_db_connection, get_system_config, get_total_fortress_hours
from datetime import datetime

st.set_page_config(page_title="Stats | Robotiator Files", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00251a; color: #e0f2f1; }
    h1 { color: #ffca28; font-size: 3rem; }
    .big-metric {
        font-size: 5rem;
        color: #ffca28;
        font-weight: bold;
        text-shadow: 3px 3px 5px #000;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Fortress Intelligence")

config = get_system_config()
year = config.get('current_year')
season = config.get('current_season')
goal = float(config.get('season_goal' if season == 'Season' else 'offseason_goal'))

total_hours = get_total_fortress_hours(year, season)

st.write(f"### Current {season} Goal Progress")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f'<div class="big-metric">{total_hours} / {goal} hrs</div>', unsafe_allow_html=True)
    progress = min(total_hours / goal, 1.0)
    st.progress(progress)

with col2:
    st.metric("Total Percent", f"{round(progress * 100, 1)}%")
    st.metric("Deployment", f"{year} {season}")

st.markdown("---")
st.header("👴 Mr. Gerstner's Presence")
conn = get_db_connection()
df_g = pd.read_sql_query("SELECT SUM(duration_seconds) / 3600.0 as total_hours FROM gerstner_logs WHERE year = ? AND season = ?",
                        conn, params=[year, season])
conn.close()
g_hours = round(df_g['total_hours'].iloc[0], 2) if not df_g.empty and df_g['total_hours'].iloc[0] else 0.0
st.metric("Total Mentor Support", f"{g_hours} Hours")

# Weekly Chart
# ... Logic to show weekly progress ...
st.info("Additional analytics can be found in the local network report.")
