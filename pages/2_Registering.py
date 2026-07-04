import dlib
import streamlit as st
if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun
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

import streamlit.components.v1 as components
import os
import base64

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
component_dir = os.path.join(parent_dir, "src", "camera_component")
face_scanner = components.declare_component("face_scanner", path=component_dir)

if "scanner_key" not in st.session_state:
    st.session_state.scanner_key = 0

st.markdown("---")
st.subheader("🤖 Biometric Profile (Optional)")
st.info("Follow the instructions on the interactive scanner to capture 5 profile angles (Straight, Left, Right, Up, Down).")

if "photos_processed" not in st.session_state or not st.session_state.reg_photos:
    scanned_images = face_scanner(key=f"face_scanner_{st.session_state.scanner_key}", height=650)
    
    if scanned_images:
        st.session_state.reg_photos = []
        failed_encodings = 0
        
        with st.spinner("Processing biometric scans..."):
            for base64_str in scanned_images:
                try:
                    header, encoded = base64_str.split(",", 1)
                    data = base64.b64decode(encoded)
                    nparr = np.frombuffer(data, np.uint8)
                    cv2_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
                    
                    encoding = encode_face(rgb_img)
                    if encoding is not None:
                        st.session_state.reg_photos.append(encoding)
                    else:
                        failed_encodings += 1
                except Exception as e:
                    failed_encodings += 1
                    
        if len(st.session_state.reg_photos) > 0:
            st.session_state.photos_processed = True
            if failed_encodings == 0:
                st.success("✅ Biometric scan complete! All 5 profile orientations registered.")
            else:
                st.warning(f"Scan complete. Registered {len(st.session_state.reg_photos)}/5 profile angles.")
            st.rerun()
        else:
            st.error("Could not detect a face in any of the scans. Please reset and try again.")
else:
    st.success(f"✅ Biometric profile loaded ({len(st.session_state.reg_photos)} profile angles registered).")
    if st.button("Reset Facial Scanner"):
        st.session_state.scanner_key += 1
        st.session_state.reg_photos = []
        if "photos_processed" in st.session_state:
            del st.session_state.photos_processed
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
                    save_encodings(user_id, st.session_state.reg_photos, conn=conn)
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
