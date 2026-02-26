from db import get_connection

def get_all_reviews(place=None, rating=None, q=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            r.*,
            u.first_name AS user_name,
            CASE WHEN r.user_id IS NULL THEN 1 ELSE 0 END AS is_anon,
            p.name AS place_name
        FROM Review r
        LEFT JOIN User u ON r.user_id = u.user_id
        JOIN Place p ON p.place_id = r.place_id
        WHERE 1=1
    """

    params = []

    if place:
        query += " AND r.place_id = %s"
        params.append(place)

    if rating:
        query += " AND r.rating = %s"
        params.append(rating)

    if q:
        query += " AND r.comment LIKE %s"
        params.append("%" + q + "%")

    query += " ORDER BY r.created_at DESC"

    cur.execute(query, tuple(params))
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return reviews



def get_review(review_id):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            r.*,
            u.first_name AS user_name,
            CASE WHEN r.user_id IS NULL THEN 1 ELSE 0 END AS is_anon,
            p.name AS place_name
        FROM Review r
        LEFT JOIN User u ON r.user_id = u.user_id
        JOIN Place p ON p.place_id = r.place_id
        WHERE r.review_id = %s
    """

    cur.execute(query, (review_id,))
    review = cur.fetchone()

    cur.close()
    conn.close()

    return review


def create_or_update_review(user_id, place_id, rating, comment):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("proc_add_review", (user_id, place_id, rating, comment))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_review(review_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Review WHERE review_id=%s", (review_id,))
    conn.commit()
    cur.close()
    conn.close()
