import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = "data/attendance.db"
LOG_TXT_PATH = "data/log.txt"

def get_db_connection():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    if not os.path.exists(DB_PATH):
        from src.init_db import init_db
        init_db()
    return sqlite3.connect(DB_PATH)

def write_plaintext_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_TXT_PATH, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def get_system_config():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_config")
    config = dict(cursor.fetchall())
    conn.close()
    return config

def log_attendance(user_id, action_type, method='PIN', capture_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    config = get_system_config()
    season = config.get('current_season', 'Offseason')
    year = int(config.get('current_year', datetime.now().year))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user_name = cursor.fetchone()[0]

    if action_type == 'login':
        cursor.execute("SELECT login_time FROM active_sessions WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            return False, "User already logged in"
        cursor.execute("INSERT INTO active_sessions (user_id, login_time, season, year, last_facial_check) VALUES (?, ?, ?, ?, ?)",
                       (user_id, now, season, year, now))
    elif action_type == 'logout':
        cursor.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))

    cursor.execute("INSERT INTO attendance_logs (user_id, type, timestamp, year, season, method, capture_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, action_type, now, year, season, method, capture_path))

    conn.commit()
    conn.close()

    write_plaintext_log(f"USER: {user_name} | ID: {user_id} | ACTION: {action_type} | METHOD: {method} | SEASON: {season} | YEAR: {year}")
    return True, f"Successfully {action_type}ed"

def get_active_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.id, users.name, active_sessions.login_time, users.nickname
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

    # Add time if currently logged in
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT login_time, season, year FROM active_sessions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        l_time, l_season, l_year = row
        if (not year or int(l_year) == int(year)) and (not season or l_season == season):
            login_dt = datetime.strptime(l_time, "%Y-%m-%d %H:%M:%S")
            duration = (datetime.now() - login_dt).total_seconds() / 3600.0
            total_hours += duration

    return round(total_hours, 2)

def get_total_fortress_hours(year, season):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    user_ids = [r[0] for r in cursor.fetchall()]
    conn.close()

    total = sum(calculate_hours_for_user(uid, year, season) for uid in user_ids)
    return round(total, 2)
