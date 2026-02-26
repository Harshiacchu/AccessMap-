from db import get_connection

def get_maintenance_for_authority(authority_id):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT MR.*, P.name AS place_name, AF.feature_type 
        FROM Maintenance_Responsibility MR
        JOIN Place P ON MR.place_id = P.place_id
        JOIN Feature_Instance FI ON MR.instance_id = FI.instance_id
        JOIN Accessibility_Feature AF ON FI.feature_id = AF.feature_id
        WHERE MR.authority_id = %s
        ORDER BY MR.since_date DESC
    """

    cur.execute(query, (authority_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


def assign_task(authority_id, place_id, instance_id, role):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Maintenance_Responsibility
        (authority_id, place_id, instance_id, role, since_date)
        VALUES (%s, %s, %s, %s, CURDATE())
    """, (authority_id, place_id, instance_id, role))

    conn.commit()
    cur.close()
    conn.close()


def delete_task(authority_id, place_id, instance_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM Maintenance_Responsibility
        WHERE authority_id=%s AND place_id=%s AND instance_id=%s
    """, (authority_id, place_id, instance_id))

    conn.commit()
    cur.close()
    conn.close()
