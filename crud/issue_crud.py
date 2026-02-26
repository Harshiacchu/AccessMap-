from db import get_connection

# -------------------------------------------------------
# FETCH ALL ISSUE REPORTS
# -------------------------------------------------------
def get_all_issues():
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT i.*, 
               u.first_name AS user_name,
               p.name AS place_name
        FROM Issue_Report i
        JOIN User u ON i.user_id = u.user_id
        JOIN Place p ON i.place_id = p.place_id
        ORDER BY i.created_at DESC
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows


# -------------------------------------------------------
# FETCH SPECIFIC ISSUE BY ID
# -------------------------------------------------------
def get_issue(report_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Issue_Report WHERE report_id=%s", (report_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


# -------------------------------------------------------
# CREATE ISSUE (CALLS STORED PROCEDURE)
# -------------------------------------------------------
def create_issue(user_id, place_id, issue_type, severity, description):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Issue_Report (user_id, place_id, issue_type, severity, description)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, place_id, issue_type, severity, description))

    conn.commit()

    report_id = cur.lastrowid   # 🔥 THIS FIXES EVERYTHING

    cur.close()
    conn.close()

    return report_id



# -------------------------------------------------------
# UPDATE ISSUE DETAILS
# -------------------------------------------------------
def update_issue(report_id, issue_type, severity, status, description):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Issue_Report
        SET issue_type=%s, severity=%s, status=%s, description=%s
        WHERE report_id=%s
    """, (issue_type, severity, status, description, report_id))

    conn.commit()
    cur.close()
    conn.close()


# -------------------------------------------------------
# RESOLVE ISSUE (AUTHORITY ONLY — uses stored procedure)
# -------------------------------------------------------
def resolve_issue(report_id, authority_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.callproc("proc_resolve_issue", (report_id, authority_id))
    conn.commit()

    cur.close()
    conn.close()


# -------------------------------------------------------
# DELETE ISSUE
# -------------------------------------------------------
def delete_issue(report_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Issue_Report WHERE report_id=%s", (report_id,))
    conn.commit()
    cur.close()
    conn.close()

# -------------------------------------------------------
# MAIL ISSUE
# -------------------------------------------------------
def get_issue_with_place(report_id):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT I.*, P.name AS place_name, P.city 
        FROM Issue_Report I
        JOIN Place P ON I.place_id = P.place_id
        WHERE I.report_id = %s
    """

    cur.execute(query, (report_id,))
    record = cur.fetchone()

    cur.close()
    conn.close()
    return record


def get_issue_media(report_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT media_id, url, media_type 
        FROM Issue_Media
        WHERE report_id = %s
    """, (report_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

