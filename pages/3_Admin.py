import streamlit as st
import sqlite3
import pandas as pd
from src.attendance_logic import get_system_config
import os
import shutil

st.set_page_config(page_title="Admin | Robotiator Files", layout="wide")

# Load custom CSS
try:
    with open("static/css/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except: pass

st.title("🛡️ Fortress Command Center")

# Insecure password check as requested
st.warning("⚠️ Access to this terminal is restricted to authorized coders.")
password = st.text_input("Enter Admin Override PIN", type="password")

ADMIN_PIN = "robotiators2025"

if password == ADMIN_PIN:
    st.success("Welcome, Commander.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["System Config", "Personnel", "Log Review", "Data Export", "Announcements"])

    with tab1:
        st.subheader("System Configuration")
        config = get_system_config()
        current_season = config.get('current_season', 'Offseason')
        current_year = config.get('current_year', '2025')

        col1, col2 = st.columns(2)
        with col1:
            new_season = st.selectbox("Current Operational Mode", ["Season", "Offseason"], index=0 if current_season == "Season" else 1)
        with col2:
            new_year = st.text_input("Operational Year", value=current_year)

        if st.button("Update Configuration"):
            conn = sqlite3.connect("data/attendance.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE system_config SET value = ? WHERE key = 'current_season'", (new_season,))
            cursor.execute("UPDATE system_config SET value = ? WHERE key = 'current_year'", (new_year,))
            conn.commit()
            conn.close()
            st.success("Configuration updated successfully.")

    with tab2:
        st.subheader("Active Personnel")
        conn = sqlite3.connect("data/attendance.db")
        active_df = pd.read_sql_query("""
            SELECT u.name, a.login_time, u.id
            FROM active_sessions a
            JOIN users u ON a.user_id = u.id
        """, conn)

        if not active_df.empty:
            for idx, row in active_df.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{row['name']}** (Logged in: {row['login_time']})")
                if col2.button(f"Force Logout {row['name']}", key=f"kick_{row['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM active_sessions WHERE user_id = ?", (row['id'],))
                    cursor.execute("INSERT INTO attendance_logs (user_id, type, timestamp, year, season, capture_path) VALUES (?, 'logout', DATETIME('now'), ?, ?, 'FORCE_LOGOUT')",
                                   (row['id'], current_year, current_season))
                    conn.commit()
                    st.rerun()
        else:
            st.write("No active sessions.")
        conn.close()

    with tab3:
        st.subheader("Face Recognition Review")
        capture_dir = "data/captures"
        if os.path.exists(capture_dir):
            captures = sorted(os.listdir(capture_dir), reverse=True)[:10]
            for cap in captures:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.image(os.path.join(capture_dir, cap), width=150)
                with col2:
                    st.write(f"**Filename:** {cap}")
                    parts = cap.replace(".jpg", "").split("_")
                    if len(parts) >= 2:
                        uid = parts[0]
                        st.write(f"Identified as User ID: {uid}")
                with col3:
                    if st.button("Wrong Person", key=f"wrong_{cap}"):
                        # Requirement: handle misidentification
                        # For now, we'll just log it and move the file
                        st.warning("Marked as incorrect. Logic to re-train coming soon.")
                        # Move to a 'wrong' folder
                        os.makedirs("data/wrong", exist_ok=True)
                        shutil.move(os.path.join(capture_dir, cap), os.path.join("data/wrong", cap))
                        st.rerun()
        else:
            st.write("No captures to review.")

    with tab4:
        st.subheader("Reports & Data Export")
        conn = sqlite3.connect("data/attendance.db")

        if st.button("Download Full Attendance Log (CSV)"):
            all_logs = pd.read_sql_query("""
                SELECT u.name, l.type, l.timestamp, l.year, l.season
                FROM attendance_logs l
                JOIN users u ON l.user_id = u.id
            """, conn)
            csv = all_logs.to_csv(index=False).encode('utf-8')
            st.download_button("Click to Download CSV", csv, "robotiators_attendance.csv", "text/csv")

        st.write("---")
        st.write("### USB Backup")
        if st.button("Manual USB Export"):
            import subprocess
            result = subprocess.run(["python3", "src/usb_export.py"], capture_output=True, text=True)
            st.text(result.stdout)
            if result.returncode == 0:
                st.success("Export attempt completed.")
            else:
                st.error("Export script failed.")
        conn.close()

    with tab5:
        st.subheader("Post Announcement")
        title = st.text_input("Title")
        content = st.text_area("Message")
        if st.button("Post"):
            conn = sqlite3.connect("data/attendance.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO announcements (title, content, author) VALUES (?, ?, 'Admin')", (title, content))
            conn.commit()
            conn.close()
            st.success("Posted!")

else:
    if password:
        st.error("Invalid Command Access")
