import sqlite3
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.getcwd())
from src.attendance_logic import write_plaintext_log

def calculate_gerstner_time():
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()

    # Process for "yesterday"
    yesterday_dt = datetime.now() - timedelta(days=1)
    yesterday = yesterday_dt.strftime("%Y-%m-%d")

    cursor.execute("SELECT timestamp, type, year, season FROM attendance_logs WHERE timestamp LIKE ? ORDER BY timestamp", (f"{yesterday}%",))
    logs = cursor.fetchall()

    if not logs:
        conn.close()
        return

    total_seconds = 0
    start_time = None
    count = 0

    year = 2026
    season = "Offseason"

    for ts_str, action, yr, seas in logs:
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        year, season = yr, seas

        if action == 'login':
            if count == 0:
                start_time = ts
            count += 1
        elif action == 'logout':
            count -= 1
            if count == 0 and start_time:
                duration = (ts - start_time).total_seconds()
                total_seconds += duration
                start_time = None

    # If someone was still logged in at end of day, they were caught by midnight cleanup
    # which is already in the logs as 'logout'.

    if total_seconds > 0:
        cursor.execute("INSERT INTO gerstner_logs (start_time, end_time, duration_seconds, year, season) VALUES (?, ?, ?, ?, ?)",
                       (f"{yesterday} 00:00:00", f"{yesterday} 23:59:59", int(total_seconds), year, season))
        write_plaintext_log(f"GERSTNER LOG: {yesterday} | Duration: {round(total_seconds/3600, 2)} hours")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    calculate_gerstner_time()
