import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from src.attendance_logic import calculate_hours_for_user

st.set_page_config(page_title="Stats | Robotiator Files", layout="wide")

try:
    with open("static/css/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except: pass

st.title("📊 Fortress Intelligence")

conn = sqlite3.connect("data/attendance.db")
users_df = pd.read_sql_query("SELECT id, name FROM users", conn)

st.header("🏆 Leaderboard")
leaderboard_data = []
for idx, row in users_df.iterrows():
    hours = calculate_hours_for_user(row['id'])
    leaderboard_data.append({"Name": row['name'], "Total Hours": hours})

df_leaderboard = pd.DataFrame(leaderboard_data).sort_values(by="Total Hours", ascending=False)

if not df_leaderboard.empty:
    fig = px.bar(df_leaderboard.head(10), x='Name', y='Total Hours', color='Total Hours',
                 title="Top 10 Robotiators", color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data recorded.")

st.markdown("---")
st.header("👴 Mr. Gerstner's Presence")
# Query Gerstner logs
df_gerstner = pd.read_sql_query("SELECT SUM(duration_seconds) / 3600.0 as total_hours FROM gerstner_logs", conn)
total_g_hours = df_gerstner['total_hours'].iloc[0] if not df_gerstner.empty else 0.0
st.metric("Total Mentor Support Time", f"{round(total_g_hours, 2)} Hours")

conn.close()
