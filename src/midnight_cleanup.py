import sqlite3
from datetime import datetime, timedelta

def run_midnight_cleanup():
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()

    # Find all users who are still logged in
    cursor.execute("SELECT user_id, login_time, season, year FROM active_sessions")
    active_sessions = cursor.fetchall()

    for user_id, login_time, season, year in active_sessions:
        # Rules: If they didn't log out, give them 30 minutes from when they logged in.
        login_dt = datetime.strptime(login_time, "%Y-%m-%d %H:%M:%S")
        logout_dt = login_dt + timedelta(minutes=30)

        logout_time_str = logout_dt.strftime("%Y-%m-%d %H:%M:%S")

        # Log the auto-logout
        cursor.execute("INSERT INTO attendance_logs (user_id, type, timestamp, year, season, capture_path) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, 'logout', logout_time_str, year, season, 'AUTO_LOGOUT'))

        # Remove from active sessions
        cursor.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()
    print(f"Midnight cleanup completed at {datetime.now()}")

if __name__ == "__main__":
    run_midnight_cleanup()
