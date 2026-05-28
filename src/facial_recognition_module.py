import face_recognition
import numpy as np
import sqlite3

def get_db_connection():
    return sqlite3.connect("data/attendance.db")

def encode_face(image_np):
    """
    Encodes a face from an image. Returns the encoding or None.
    """
    encodings = face_recognition.face_encodings(image_np)
    if len(encodings) == 0:
        return None
    return encodings[0]

def save_encodings(user_id, encodings_list):
    """
    Saves a list of numpy encodings for a specific user to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    for enc in encodings_list:
        encoding_bytes = enc.tobytes()
        cursor.execute("INSERT INTO facial_encodings (user_id, encoding) VALUES (?, ?)", (user_id, encoding_bytes))
    conn.commit()
    conn.close()

def identify_face(image_np, tolerance=0.5):
    """
    Identifies a face from an image by comparing it with known encodings in the database.
    Returns user_id if found, else None.
    """
    unknown_encodings = face_recognition.face_encodings(image_np)
    if len(unknown_encodings) == 0:
        return None, "No face detected"

    unknown_encoding = unknown_encodings[0]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, encoding FROM facial_encodings")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None, "No registered faces in database"

    known_encodings = []
    user_ids = []
    for row in rows:
        user_ids.append(row[0])
        known_encodings.append(np.frombuffer(row[1], dtype=np.float64))

    matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=tolerance)

    if True in matches:
        # Find all matches and use the one with smallest distance
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return user_ids[best_match_index], "Match found"

    return None, "No match found"
