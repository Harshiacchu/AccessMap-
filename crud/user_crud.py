from db import get_connection
from werkzeug.security import generate_password_hash

def register_user(first_name, last_name, email, password, disability_type):
    conn = get_connection()
    cur = conn.cursor()

    # Check existing email
    cur.execute("SELECT user_id FROM User WHERE email=%s", (email,))
    exists = cur.fetchone()

    if exists:
        cur.close()
        conn.close()
        return False  # user already exists

    hashed = generate_password_hash(password)

    query = """
        INSERT INTO User (first_name, last_name, email, password_hash, disability_type)
        VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(query, (first_name, last_name, email, hashed, disability_type))
    conn.commit()

    cur.close()
    conn.close()
    return True
