import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "data/attendance.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_system_config():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_config")
    config = dict(cursor.fetchall())
    conn.close()
    return config

def log_attendance(user_id, action_type, capture_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    config = get_system_config()
    season = config.get('current_season', 'Offseason')
    year = int(config.get('current_year', datetime.now().year))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action_type == 'login':
        cursor.execute("SELECT login_time FROM active_sessions WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            return False, "User already logged in"
        cursor.execute("INSERT INTO active_sessions (user_id, login_time, season, year) VALUES (?, ?, ?, ?)",
                       (user_id, now, season, year))
    elif action_type == 'logout':
        cursor.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))

    cursor.execute("INSERT INTO attendance_logs (user_id, type, timestamp, year, season, capture_path) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, action_type, now, year, season, capture_path))

    conn.commit()
    conn.close()
    return True, f"Successfully {action_type}ed"

def get_active_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.id, users.name, active_sessions.login_time
        FROM active_sessions
        JOIN users ON active_sessions.user_id = users.id
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def calculate_hours_for_user(user_id, year=None, season=None):
    conn = get_db_connection()
    query = "SELECT timestamp, type FROM attendance_logs WHERE user_id = ?"
    params = [user_id]
    if year:
        query += " AND year = ?"
        params.append(year)
    if season:
        query += " AND season = ?"
        params.append(season)
    query += " ORDER BY timestamp"

    logs = pd.read_sql_query(query, conn, params=params)
    conn.close()

    total_hours = 0.0
    login_time = None

    for _, row in logs.iterrows():
        ts = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
        if row['type'] == 'login':
            login_time = ts
        elif row['type'] == 'logout' and login_time:
            duration = (ts - login_time).total_seconds() / 3600.0
            total_hours += duration
            login_time = None

    return round(total_hours, 2)
