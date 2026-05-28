import streamlit as st
import sqlite3
import cv2
import numpy as np
from src.facial_recognition_module import identify_face
from src.attendance_logic import log_attendance, get_active_users, get_db_connection
from datetime import datetime
import time

st.set_page_config(page_title="Logging | Robotiator Files", layout="centered")

# Custom CSS for Success Flash and Theme
st.markdown("""
    <style>
    @keyframes flash-green {
        0% { background-color: transparent; }
        50% { background-color: rgba(46, 125, 50, 0.8); }
        100% { background-color: transparent; }
    }
    .flash-active {
        animation: flash-green 0.5s ease-in-out 2;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: 9999;
        pointer-events: none;
    }
    .stApp {
        background-color: #00251a;
        color: #e0f2f1;
    }
    h1 { color: #ffca28; }
    .last-logs {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

if "flash" not in st.session_state:
    st.session_state.flash = False

if st.session_state.flash:
    st.markdown('<div class="flash-active"></div>', unsafe_allow_html=True)
    st.session_state.flash = False

st.title("🛡️ Fortress Access Station")

# --- PIN ENTRY (PRIMARY) ---
st.header("🔑 PIN Access")
pin_input = st.text_input("Enter your PIN", type="password", max_chars=10)
if st.button("Log In/Out"):
    if len(pin_input) >= 4:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE pin = ?", (pin_input,))
        user = cursor.fetchone()
        conn.close()

        if user:
            uid, uname = user
            active_ids = [u[0] for u in get_active_users()]
            action = 'logout' if uid in active_ids else 'login'
            success, msg = log_attendance(uid, action, method='PIN')
            if success:
                st.success(f"Access {action}ed for {uname}!")
                st.session_state.flash = True
                st.rerun()
            else:
                st.error(msg)
        else:
            st.error("Invalid PIN.")
    else:
        st.warning("PIN must be at least 4 digits.")

st.markdown("---")

# --- FACIAL RECOGNITION (SECONDARY) ---
with st.expander("🤖 Optional: Facial Recognition"):
    st.info("Ensure you are the closest person to the camera.")
    img_file = st.camera_input("Biometric Scan")
    if img_file:
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        uid, msg = identify_face(rgb_img)
        if uid:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users WHERE id = ?", (uid,))
            uname = cursor.fetchone()[0]
            conn.close()

            active_ids = [u[0] for u in get_active_users()]
            action = 'logout' if uid in active_ids else 'login'
            success, log_msg = log_attendance(uid, action, method='Face')
            if success:
                st.success(f"Biometrics Verified: {uname}! {action} successful.")
                st.session_state.flash = True
                st.rerun()
            else:
                st.error(log_msg)
        else:
            st.warning(f"Scan result: {msg}")

# --- RECENT EVENTS ---
st.markdown("---")
st.subheader("🕙 Recent Activity")
conn = get_db_connection()
recent_logs = pd.read_sql_query("""
    SELECT u.name, l.type, l.timestamp
    FROM attendance_logs l
    JOIN users u ON l.user_id = u.id
    ORDER BY l.timestamp DESC LIMIT 5
""", conn)
conn.close()

if not recent_logs.empty:
    for _, row in recent_logs.iterrows():
        st.write(f"✅ **{row['name']}** {row['type']}ed at {row['timestamp'][11:16]}")
else:
    st.write("No recent activity.")
