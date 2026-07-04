import streamlit as st
if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun
import time
import pandas as pd
from src.attendance_logic import get_db_connection, get_system_config, get_total_fortress_hours, calculate_hours_for_user

st.set_page_config(page_title="KIOSK | Robotiator Files", layout="wide")

# Theme & Refresh
st.markdown("""
    <style>
    .stApp { background-color: #00251a; color: #e0f2f1; }
    .kiosk-header { color: #ffca28; font-size: 4rem; text-align: center; margin-bottom: 0px;}
    .kiosk-metric { font-size: 8rem; color: #ffca28; text-align: center; font-weight: bold; text-shadow: 4px 4px 6px #000;}
    .leader-table { font-size: 1.5rem; width: 100%; border-collapse: collapse; }
    .leader-table td { padding: 10px; border-bottom: 1px solid rgba(255,202,40,0.2); }
    .personnel-here { background: rgba(46, 125, 50, 0.3); padding: 10px; border-radius: 10px; margin: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Auto-refresh every 30 seconds to update time accurately
# and check for new events.
# We use a placeholder for now as streamlit_autorefresh isn't installed.
# But we can use time.sleep and st.rerun for a kiosk.
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

config = get_system_config()
year = config.get('current_year')
season = config.get('current_season')
goal = float(config.get('season_goal' if season == 'Season' else 'offseason_goal'))

total_hours = get_total_fortress_hours(year, season)

col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown(f'<div class="kiosk-header">{season} Progress</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kiosk-metric">{total_hours} / {int(goal)}</div>', unsafe_allow_html=True)
    st.progress(min(total_hours / goal, 1.0))

    st.markdown("---")
    st.header("🏆 Top Contributors")
    conn = get_db_connection()
    users = pd.read_sql_query("SELECT id, name, nickname FROM users", conn)
    conn.close()

    data = []
    for _, user in users.iterrows():
        hours = calculate_hours_for_user(user['id'], year, season)
        data.append({"Personnel": user['nickname'] or user['name'], "Hours": hours})
    
    if data:
        df = pd.DataFrame(data).sort_values(by="Hours", ascending=False).head(10)
    else:
        df = pd.DataFrame(columns=["Personnel", "Hours"])

    st.table(df)

with col_side:
    st.header("📍 Personnel Present")
    conn = get_db_connection()
    active = pd.read_sql_query("SELECT u.name, u.nickname FROM active_sessions a JOIN users u ON a.user_id = u.id", conn)
    conn.close()

    if not active.empty:
        for _, row in active.iterrows():
            st.markdown(f'<div class="personnel-here">👤 {row["nickname"] or row["name"]}</div>', unsafe_allow_html=True)
    else:
        st.write("Fortress is currently empty.")

# Simple refresh logic
time.sleep(30)
st.rerun()
