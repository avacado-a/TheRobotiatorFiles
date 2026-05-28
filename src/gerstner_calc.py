import sqlite3
from datetime import datetime, timedelta

def calculate_gerstner_time():
    """
    Mr. Gerstner's time starts when the first person logs in and ends when the last person logs out.
    We process this daily to keep his logs up to date.
    """
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()

    # Get all logs from the previous day that haven't been processed for Gerstner
    # This is a bit complex for a stateless script, so we'll simplify:
    # We find all login/logout events and calculate 'union' of time intervals.

    # Logic:
    # 1. Get all attendance logs for 'yesterday'
    # 2. Sort by timestamp
    # 3. Use a counter: +1 for login, -1 for logout
    # 4. Timer starts when counter goes 0 -> 1
    # 5. Timer stops when counter goes 1 -> 0
    # 6. Sum these intervals.

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute("SELECT timestamp, type, year, season FROM attendance_logs WHERE timestamp LIKE ? ORDER BY timestamp", (f"{yesterday}%",))
    logs = cursor.fetchall()

    total_seconds = 0
    start_time = None
    count = 0

    current_year = 2025
    current_season = "Offseason"

    for ts_str, action, yr, seas in logs:
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        current_year = yr
        current_season = seas

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

    if total_seconds > 0:
        cursor.execute("INSERT INTO gerstner_logs (start_time, end_time, duration_seconds, year, season) VALUES (?, ?, ?, ?, ?)",
                       (f"{yesterday} 00:00:00", f"{yesterday} 23:59:59", int(total_seconds), current_year, current_season))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    calculate_gerstner_time()
