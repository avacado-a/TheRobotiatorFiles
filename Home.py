import streamlit as st
import sqlite3
import cv2
import numpy as np
from src.attendance_logic import get_active_users, get_system_config
import os
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

st.set_page_config(page_title="The Robotiator Files", layout="wide", page_icon="🗿")

# Load custom CSS
with open("static/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Define shared CSS classes
st.markdown("""
    <style>
    .success-box {
        padding: 10px;
        border-radius: 10px;
        background-color: rgba(46, 125, 50, 0.8);
        color: white;
        margin: 5px 0;
        border: 1px solid #81c784;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🗿 THE ROBOTIATOR FILES 🤖")
st.subheader("🌴 Tropical Fortress HQ")

# Hero Section
col1, col2 = st.columns([2, 1])

with col1:
    st.image("https://img.icons8.com/color/144/robot-2.png", width=100) # Placeholder for logo
    st.markdown("""
    ### Welcome, Robotiator!
    Ensure you log in/out at the **Logging** station.
    The fortress is currently active.
    """)

with col2:
    local_ip = get_local_ip()
    st.info(f"📱 **Mobile Login**\n\nScan or visit:\n`http://{local_ip}:8501`")
    st.info(f"🎥 **Live Feed**\n\nView Fortress Feed:\n`http://{local_ip}:5000/video_feed`")

# Announcements
st.sidebar.title("📡 Announcements")
conn = sqlite3.connect("data/attendance.db")
cursor = conn.cursor()
cursor.execute("SELECT title, content, created_at FROM announcements ORDER BY created_at DESC LIMIT 5")
announcements = cursor.fetchall()
for ann in announcements:
    with st.sidebar.expander(f"📢 {ann[0]}"):
        st.write(ann[1])
        st.caption(f"Posted: {ann[2]}")

# Who's Here Now
st.markdown("---")
st.header("📍 Current Personnel in Fortress")
active_users = get_active_users()
if active_users:
    cols = st.columns(4)
    for i, user in enumerate(active_users):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="success-box">
                <b>👤 {user[1]}</b><br>
                <small>In: {user[2][11:16]}</small>
            </div>
            """, unsafe_allow_html=True)
else:
    st.write("🍃 The fortress is quiet. No personnel detected.")

st.markdown("---")
st.caption("v2.0 | Built for the Robotiators | No maintenance required.")
conn.close()
