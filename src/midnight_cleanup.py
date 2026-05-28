import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())
from src.attendance_logic import write_plaintext_log

def run_midnight_cleanup():
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()

    # Get current season/year
    cursor.execute("SELECT key, value FROM system_config")
    config = dict(cursor.fetchall())
    season = config.get('current_season', 'Offseason')
    year = int(config.get('current_year', 2026))

    # Find all users who are still logged in
    cursor.execute("SELECT user_id, login_time FROM active_sessions")
    active_sessions = cursor.fetchall()

    for user_id, login_time in active_sessions:
        # Rule: login + 30 minutes
        login_dt = datetime.strptime(login_time, "%Y-%m-%d %H:%M:%S")
        logout_dt = login_dt + timedelta(minutes=30)
        logout_time_str = logout_dt.strftime("%Y-%m-%d %H:%M:%S")

        # Log the auto-logout
        cursor.execute("INSERT INTO attendance_logs (user_id, type, timestamp, year, season, method, capture_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (user_id, 'logout', logout_time_str, year, season, 'AUTO_LOGOUT', None))

        # Remove from active sessions
        cursor.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))

        write_plaintext_log(f"AUTO-LOGOUT: User ID {user_id} | Logged out at {logout_time_str} (30 min rule)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_midnight_cleanup()
