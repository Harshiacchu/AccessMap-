from db import get_connection
from werkzeug.security import generate_password_hash

# List all authorities
def get_all_authorities():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Authority")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


# Get authority by id
def get_authority(authority_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Authority WHERE authority_id=%s", (authority_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data


# Create authority (admin function only)
def create_authority(first, last, email, phone, password):
    conn = get_connection()
    cur = conn.cursor()

    # Check existing authority (by email OR phone)
    cur.execute("SELECT authority_id FROM Authority WHERE email=%s OR phone=%s", (email, phone))
    exists = cur.fetchone()

    if exists:
        cur.close()
        conn.close()
        return False  # already exists

    hashed = generate_password_hash(password)

    cur.execute("""
        INSERT INTO Authority(first_name, last_name, email, phone, password_hash)
        VALUES (%s, %s, %s, %s, %s)
    """, (first, last, email, phone, hashed))

    conn.commit()
    cur.close()
    conn.close()
    return True

# Update authority
def update_authority(authority_id, first, last, email, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Authority 
        SET first_name=%s, last_name=%s, email=%s, phone=%s
        WHERE authority_id=%s
    """, (first, last, email, phone, authority_id))

    conn.commit()
    cur.close()
    conn.close()


# Delete authority
def delete_authority(authority_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Authority WHERE authority_id=%s", (authority_id,))
    conn.commit()
    cur.close()
    conn.close()
