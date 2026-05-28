import streamlit as st
import sqlite3
import pandas as pd
import cv2
import numpy as np
from src.facial_recognition_module import identify_face
from src.attendance_logic import log_attendance, get_active_users
from datetime import datetime
import os

st.set_page_config(page_title="Logging | Robotiator Files", layout="centered")

st.title("⏱️ Attendance Station")

# Webcam feed for identification
st.write("### 🤖 Facial Recognition")
img_file = st.camera_input("Look at the camera for 1-3 seconds")

if img_file:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    with st.spinner("Analyzing biometric data..."):
        user_id, msg = identify_face(rgb_img)

    if user_id:
        conn = sqlite3.connect("data/attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        user_name = cursor.fetchone()[0]
        conn.close()

        # Save capture for admin review
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        capture_path = f"data/captures/{user_id}_{timestamp}.jpg"
        cv2.imwrite(capture_path, cv2_img)

        # Check if login or logout
        active_users = [u[0] for u in get_active_users()]
        action = 'logout' if user_id in active_users else 'login'

        success, log_msg = log_attendance(user_id, action, capture_path)
        if success:
            st.success(f"Verified: {user_name}! {log_msg}.")
            st.balloons()
        else:
            st.error(log_msg)
    else:
        st.warning("Identification failed. Please ensure your face is well-lit or use your PIN below.")

st.markdown("---")

# PIN Backup
with st.expander("🔑 Manual PIN Entry"):
    st.write("Use this if facial recognition is not working.")
    pin_input = st.text_input("Enter your PIN", type="password")
    if st.button("Log In/Out with PIN"):
        conn = sqlite3.connect("data/attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE pin = ?", (pin_input,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, user_name = user
            active_users = [u[0] for u in get_active_users()]
            action = 'logout' if user_id in active_users else 'login'
            success, log_msg = log_attendance(user_id, action, 'PIN_ENTRY')
            if success:
                st.success(f"Verified: {user_name}! {log_msg}.")
            else:
                st.error(log_msg)
        else:
            st.error("Invalid PIN.")
