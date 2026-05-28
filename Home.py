import streamlit as st
import sqlite3
import pandas as pd
from src.attendance_logic import get_db_connection, get_system_config

st.set_page_config(page_title="Guide | Robotiator Files", layout="wide")

# Theme
st.markdown("""
    <style>
    .stApp { background-color: #00251a; color: #e0f2f1; }
    h1, h2 { color: #ffca28; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗿 The Robotiator Files")
st.subheader("🌴 Tropical Fortress Operations Guide")

st.markdown("""
### 🏗️ Mission Control
Welcome to the overhaul of the Robotiators Attendance System. This station is built to last and requires zero maintenance.

### 🔑 How to Access the Fortress
1. **Registration**: Go to the `Registering` page. Enter your full name and a PIN (4+ digits). You can optionally scan your face 5 times to enable biometrics.
2. **Logging**:
   - **PIN**: The primary way to log in/out. Enter your PIN and click the button.
   - **Biometrics**: If you registered your face, look at the camera for 1-3 seconds. The system detects the closest person.
3. **Kiosk**: The main monitor displays real-time hours and the leaderboard. It auto-refreshes when personnel enter or leave.

### 📊 Intelligence Tracking
- **Leaderboard**: See who has the most hours in the current season.
- **Statistics**: View the total progress towards the seasonal goal (5000 hours in Season, 888 in Offseason).
- **Admin**: For command override. Use PIN `RobotiatorFiles888`.

### 🛡️ System Robustness
- **Auto-Logout**: If you forget to log out, the system automatically logs you out at midnight and gives you exactly 30 minutes from your login time.
- **Backups**: Every event is logged in a plaintext file and the database. Data is easily exportable to USB in the Admin panel.
""")

st.info("Built for the Robotiators | No Maintenance Required.")
