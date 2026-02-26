from db import get_connection

# ============================================
# GET ALL FEATURES INSTALLED AT A PLACE
# ============================================
def get_features_for_place(place_id):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT FI.instance_id, FI.status, FI.last_checked,
               AF.feature_type, AF.description
        FROM Feature_Instance FI
        JOIN Accessibility_Feature AF ON FI.feature_id = AF.feature_id
        WHERE FI.place_id = %s
        ORDER BY AF.feature_type;
    """

    cur.execute(query, (place_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# ============================================
# ADD A NEW FEATURE INSTANCE TO A PLACE
# ============================================
def add_feature_instance(place_id, feature_id, status):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO Feature_Instance (place_id, feature_id, status)
        VALUES (%s, %s, %s)
    """

    cur.execute(query, (place_id, feature_id, status))
    conn.commit()

    cur.close()
    conn.close()


# ============================================
# UPDATE FEATURE INSTANCE STATUS
# ============================================
def update_feature_instance(instance_id, status):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        UPDATE Feature_Instance
        SET status = %s, last_checked = NOW()
        WHERE instance_id = %s
    """

    cur.execute(query, (status, instance_id))
    conn.commit()

    cur.close()
    conn.close()


# ============================================
# DELETE FEATURE INSTANCE
# ============================================
def delete_feature_instance(instance_id):
    conn = get_connection()
    cur = conn.cursor()

    query = "DELETE FROM Feature_Instance WHERE instance_id = %s"
    cur.execute(query, (instance_id,))
    conn.commit()

    cur.close()
    conn.close()
