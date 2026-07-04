import dlib
import face_recognition
import numpy as np
import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    return sqlite3.connect("data/attendance.db")

def encode_face(image_np):
    encodings = face_recognition.face_encodings(image_np)
    if len(encodings) == 0:
        return None
    return encodings[0]

def save_encodings(user_id, encodings_list, conn=None):
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    cursor = conn.cursor()
    for enc in encodings_list:
        encoding_bytes = enc.tobytes()
        cursor.execute("INSERT INTO facial_encodings (user_id, encoding) VALUES (?, ?)", (user_id, encoding_bytes))
    if should_close:
        conn.commit()
        conn.close()

def identify_face(image_np, tolerance=0.45):
    """
    Identifies the BIGGEST face in view, with a 10-minute cooldown per user.
    Returns (user_id, message, face_location)
    """
    face_locations = face_recognition.face_locations(image_np)
    if not face_locations:
        return None, "No face detected", None

    # Find the biggest face (by area)
    # location is (top, right, bottom, left)
    biggest_face_idx = 0
    max_area = 0
    for i, (top, right, bottom, left) in enumerate(face_locations):
        area = (bottom - top) * (right - left)
        if area > max_area:
            max_area = area
            biggest_face_idx = i

    biggest_face_location = face_locations[biggest_face_idx]
    unknown_encodings = face_recognition.face_encodings(image_np, [biggest_face_location])

    if not unknown_encodings:
        return None, "Encoding failed", biggest_face_location

    unknown_encoding = unknown_encodings[0]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, encoding FROM facial_encodings")
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return None, "No registered faces", biggest_face_location

    known_encodings = []
    user_ids = []
    for row in rows:
        user_ids.append(row[0])
        known_encodings.append(np.frombuffer(row[1], dtype=np.float64))

    matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=tolerance)

    if True in matches:
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            uid = user_ids[best_match_index]

            # Cooldown check: Last log for this user within 10 minutes
            cursor.execute("SELECT timestamp FROM attendance_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (uid,))
            last_log = cursor.fetchone()
            if last_log:
                last_ts = datetime.strptime(last_log[0], "%Y-%m-%d %H:%M:%S")
                if datetime.now() - last_ts < timedelta(minutes=10):
                    conn.close()
                    return None, "Cooldown active", biggest_face_location

            conn.close()
            return uid, "Match found", biggest_face_location

    conn.close()
    return None, "No match found", biggest_face_location
