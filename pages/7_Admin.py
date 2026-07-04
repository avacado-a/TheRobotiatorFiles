import streamlit as st
if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun
import sqlite3
import pandas as pd
from src.attendance_logic import get_system_config, get_db_connection
import os
import shutil

st.set_page_config(page_title="Admin | Robotiator Files", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00251a; color: #e0f2f1; }
    h1 { color: #ffca28; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Command Override")

password = st.text_input("Enter Command Access PIN", type="password")
ADMIN_PIN = "RobotiatorFiles888"

if password == ADMIN_PIN:
    st.success("Welcome, Commander.")

    tab1, tab2, tab3, tab4 = st.tabs(["System Config", "Personnel Management", "Log Review", "Data Export"])

    with tab1:
        st.subheader("Deployment Configuration")
        config = get_system_config()
        current_season = config.get('current_season')
        current_year = config.get('current_year')

        new_season = st.selectbox("Switch Operational Mode", ["Season", "Offseason"], index=0 if current_season == "Season" else 1)
        new_year = st.text_input("Operational Year", value=current_year)

        if st.button("Apply Changes"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE system_config SET value = ? WHERE key = 'current_season'", (new_season,))
            cursor.execute("UPDATE system_config SET value = ? WHERE key = 'current_year'", (new_year,))
            conn.commit()
            conn.close()

            if new_season == "Offseason" and current_season == "Season":
                st.warning("Season ended. Report should be downloaded.")
                # Logic to trigger download would go here

            st.success("Config updated.")
            st.rerun()

    with tab2:
        st.subheader("Personnel Registry")
        conn = get_db_connection()
        users_df = pd.read_sql_query("SELECT id, name, nickname, pin FROM users", conn)
        st.dataframe(users_df)

        st.write("---")
        st.subheader("Edit Personnel")
        user_to_edit = st.selectbox("Select User", users_df['name'].tolist())
        if user_to_edit:
            u_row = users_df[users_df['name'] == user_to_edit].iloc[0]
            new_name = st.text_input("Change Name", value=u_row['name'])
            new_nick = st.text_input("Change Nickname", value=u_row['nickname'] or "")
            new_pin = st.text_input("Reset PIN", value=u_row['pin'])

            if st.button("Save Personnel Changes"):
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET name=?, nickname=?, pin=? WHERE id=?", (new_name, new_nick, new_pin, int(u_row['id'])))
                conn.commit()
                st.success("Saved.")
                st.rerun()
        conn.close()

    with tab3:
        st.subheader("Recent Captures")
        cap_dir = "data/captures"
        if os.path.exists(cap_dir):
            caps = os.listdir(cap_dir)[:10]
            for cap in caps:
                st.image(os.path.join(cap_dir, cap), width=200)
                if st.button(f"Mark Incorrect: {cap}"):
                    # Correction logic
                    pass

    with tab4:
        st.subheader("Data Portability")
        if st.button("Export Full Database to USB"):
            import subprocess
            res = subprocess.run(["python3", "src/usb_export.py"], capture_output=True, text=True)
            st.text(res.stdout)

else:
    if password:
        st.error("Access Denied.")
