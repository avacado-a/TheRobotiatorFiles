import streamlit as st
import sqlite3
import cv2
import numpy as np
from src.facial_recognition_module import encode_face, save_encodings
from src.attendance_logic import get_db_connection

st.set_page_config(page_title="Register | Robotiator Files", layout="centered")

st.title("📝 Join the Robotiators")

if "reg_photos" not in st.session_state:
    st.session_state.reg_photos = []

name = st.text_input("Full Name")
nickname = st.text_input("Nickname (Optional)")
pin = st.text_input("Create a numeric PIN (4+ digits)", type="password")

st.markdown("---")
st.subheader("🤖 Biometric Profile (Optional)")
st.info("Capture 5 photos to enable facial recognition login.")

img_file = st.camera_input("Face Scan")

if img_file and len(st.session_state.reg_photos) < 5:
    if st.button(f"Add Photo {len(st.session_state.reg_photos) + 1}"):
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        encoding = encode_face(rgb_img)
        if encoding is not None:
            st.session_state.reg_photos.append(encoding)
            st.success("Photo added!")
            st.rerun()
        else:
            st.error("Face not found. Please try again.")

if st.button("Clear Biometric Data"):
    st.session_state.reg_photos = []
    st.rerun()

st.markdown("---")
if name and pin:
    if st.button("Complete Registration"):
        if not pin.isdigit() or len(pin) < 4:
            st.error("PIN must be at least 4 digits (numbers only).")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, nickname, pin) VALUES (?, ?, ?)", (name, nickname, pin))
                user_id = cursor.lastrowid
                if st.session_state.reg_photos:
                    save_encodings(user_id, st.session_state.reg_photos)
                conn.commit()
                st.balloons()
                st.success(f"Welcome to the Fortress, {name}!")
                st.session_state.reg_photos = []
            except Exception as e:
                st.error(f"Error during registration: {e}")
            finally:
                conn.close()
else:
    st.info("Please enter your name and PIN to register.")
