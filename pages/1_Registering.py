import streamlit as st
import cv2
import numpy as np
import sqlite3
from src.facial_recognition_module import encode_face, save_encodings

st.set_page_config(page_title="Register | Robotiator Files", layout="centered")

st.title("📝 New Robotiator Registration")

if "reg_photos" not in st.session_state:
    st.session_state.reg_photos = []

name = st.text_input("Full Name (First and Last)")
pin = st.text_input("Create a 4-digit PIN", type="password", max_chars=4)

st.write("---")
st.write(f"### Face Capture ({len(st.session_state.reg_photos)}/5)")
st.info("Capture 5 photos from slightly different angles for better accuracy.")

img_file = st.camera_input("Look at the camera")

if img_file and len(st.session_state.reg_photos) < 5:
    if st.button("Add Photo"):
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        encoding = encode_face(rgb_img)
        if encoding is not None:
            st.session_state.reg_photos.append(encoding)
            st.success(f"Captured photo {len(st.session_state.reg_photos)}!")
            st.rerun()
        else:
            st.error("No face detected. Try again.")

if st.button("Reset Photos"):
    st.session_state.reg_photos = []
    st.rerun()

if len(st.session_state.reg_photos) >= 3 and name and pin:
    if st.button("Submit Registration"):
        conn = sqlite3.connect("data/attendance.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, pin) VALUES (?, ?)", (name, pin))
            user_id = cursor.lastrowid
            save_encodings(user_id, st.session_state.reg_photos)
            conn.commit()
            st.balloons()
            st.success(f"Welcome to the Robotiators, {name}!")
            st.session_state.reg_photos = []
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            conn.close()
