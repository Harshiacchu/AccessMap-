# crud/feature_crud.py
from db import get_connection

def get_all_features():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Accessibility_Feature ORDER BY feature_type")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_feature(feature_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Accessibility_Feature WHERE feature_id=%s", (feature_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_feature(feature_type, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Accessibility_Feature (feature_type, description)
        VALUES (%s, %s)
    """, (feature_type, description))
    conn.commit()
    cur.close()
    conn.close()

def update_feature(feature_id, feature_type, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Accessibility_Feature
        SET feature_type=%s, description=%s
        WHERE feature_id=%s
    """, (feature_type, description, feature_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_feature(feature_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Accessibility_Feature WHERE feature_id=%s", (feature_id,))
    conn.commit()
    cur.close()
    conn.close()
