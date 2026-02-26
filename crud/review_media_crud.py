# crud/review_media_crud.py
from db import get_connection

def add_review_media(review_id, url, media_type):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Review_Media (review_id, url, media_type)
        VALUES (%s, %s, %s)
    """, (review_id, url, media_type))

    conn.commit()
    cur.close()
    conn.close()


def get_review_media(review_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM Review_Media
        WHERE review_id = %s
        ORDER BY uploaded_at DESC
    """, (review_id,))

    media = cur.fetchall()
    cur.close()
    conn.close()
    return media


def delete_review_media(media_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM Review_Media WHERE media_id = %s", (media_id,))
    conn.commit()

    cur.close()
    conn.close()
