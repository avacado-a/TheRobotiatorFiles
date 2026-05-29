import streamlit as st
import sqlite3
import cv2
import numpy as np
import pandas as pd
from src.facial_recognition_module import identify_face
from src.attendance_logic import log_attendance, get_active_users, get_db_connection
from datetime import datetime
import time

st.set_page_config(page_title="Logging | Robotiator Files", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #00251a; color: #e0f2f1; }
    h1 { color: #ffca28; text-align: center; }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Fortress Access Station")

col_feed, col_side = st.columns([2, 1])

with col_feed:
    st.subheader("🤖 Biometric Auto-Scanner")
    frame_placeholder = st.empty()
    status_placeholder = st.empty()

with col_side:
    st.subheader("🔑 PIN Access")
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
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Invalid PIN.")
        else:
            st.warning("PIN must be at least 4 digits.")

    st.markdown("---")
    st.subheader("🕙 Recent Activity")
    conn = get_db_connection()
    recent_logs = pd.read_sql_query("""
        SELECT u.name, l.type, l.timestamp
        FROM attendance_logs l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.timestamp DESC LIMIT 8
    """, conn)
    conn.close()

    if not recent_logs.empty:
        for _, row in recent_logs.iterrows():
            st.write(f"✅ **{row['name']}** {row['type']}ed at {row['timestamp'][11:16]}")
    else:
        st.write("No recent activity.")

# --- AUTO-SCANNER LOOP ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    status_placeholder.error("Error: Could not access camera.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            status_placeholder.error("Error: Camera feed lost.")
            break

        # Convert for identification
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Identity Check
        uid, msg, location = identify_face(rgb_frame)

        # Draw UI on frame
        if location:
            top, right, bottom, left = location
            color = (0, 255, 0) if uid else (255, 202, 40) # Green if matched, Gold if just face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            if uid:
                cv2.putText(frame, "MATCH FOUND", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            elif msg == "Cooldown active":
                cv2.putText(frame, "COOLDOWN", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Update Placeholder
        frame_placeholder.image(frame, channels="BGR", use_container_width=True)

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
                status_placeholder.markdown(f'<div class="status-box" style="background-color: rgba(46, 125, 50, 0.8);">Welcome back, {uname}! {action.capitalize()} Success.</div>', unsafe_allow_html=True)
                cap.release()
                time.sleep(3)
                st.rerun()

        # Small pause to prevent extreme CPU usage
        time.sleep(0.01)

cap.release()
