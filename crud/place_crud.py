# crud/place_crud.py
from db import get_connection

# ----------------------------
# CREATE PLACE
# ----------------------------
def create_place(data):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO Place 
        (name, country, state, city, street, zip_code, category, latitude, longitude, verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        data["name"],
        data["country"],
        data["state"],
        data["city"],
        data["street"],
        data["zip_code"],
        data["category"],
        data["latitude"],
        data["longitude"],
        data["verified"],
    ))

    conn.commit()
    cur.close()
    conn.close()


# ----------------------------
# READ ALL PLACES
# ----------------------------
def get_all_places():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Place ORDER BY created_at DESC")
    places = cur.fetchall()

    cur.close()
    conn.close()
    return places


# ----------------------------
# READ SINGLE PLACE
# ----------------------------
def get_place(place_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Place WHERE place_id = %s", (place_id,))
    place = cur.fetchone()

    cur.close()
    conn.close()
    return place


# ----------------------------
# UPDATE PLACE
# ----------------------------
def update_place(place_id, data):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        UPDATE Place SET 
        name=%s, country=%s, state=%s, city=%s, street=%s, 
        zip_code=%s, category=%s, latitude=%s, longitude=%s, verified=%s
        WHERE place_id=%s
    """

    cur.execute(query, (
        data["name"], data["country"], data["state"], data["city"],
        data["street"], data["zip_code"], data["category"],
        data["latitude"], data["longitude"], data["verified"],
        place_id
    ))

    conn.commit()
    cur.close()
    conn.close()


# ----------------------------
# DELETE PLACE
# ----------------------------
def delete_place(place_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM Place WHERE place_id=%s", (place_id,))
    conn.commit()

    cur.close()
    conn.close()
