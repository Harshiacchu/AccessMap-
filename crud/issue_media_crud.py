from db import get_connection

def add_issue_media(report_id, url, media_type):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Issue_Media (report_id, url, media_type)
        VALUES (%s, %s, %s)
    """, (report_id, url, media_type))

    conn.commit()
    cur.close()
    conn.close()


def get_issue_media(report_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Issue_Media WHERE report_id=%s", (report_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


def delete_issue_media_db(media_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM Issue_Media WHERE media_id=%s", (media_id,))

    conn.commit()
    cur.close()
    conn.close()
