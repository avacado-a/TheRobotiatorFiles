import sqlite3
import os

DB_PATH = "data/attendance.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        pin TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Facial Encodings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS facial_encodings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        encoding BLOB NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Attendance Logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT CHECK(type IN ('login', 'logout')),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        year INTEGER,
        season TEXT,
        capture_path TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Active Sessions (to track who is currently here)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS active_sessions (
        user_id INTEGER PRIMARY KEY,
        login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        season TEXT,
        year INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Mr. Gerstner's Logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gerstner_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time DATETIME,
        end_time DATETIME,
        duration_seconds INTEGER,
        year INTEGER,
        season TEXT
    )
    ''')

    # Announcements
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        author TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # System Configuration
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # Default Config
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('current_season', 'Offseason')")
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('current_year', '2025')")
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('admin_password', 'robotiators2025')")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    init_db()
    print("Database initialized successfully.")
