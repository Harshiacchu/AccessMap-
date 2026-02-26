# app.py
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from db import get_connection
from config import SECRET_KEY
from crud.issue_crud import get_issue_with_place
from werkzeug.security import check_password_hash
from crud.user_crud import register_user


from crud.review_media_crud import (
    add_review_media,
    get_review_media,
    delete_review_media
)

from crud.issue_media_crud import add_issue_media, get_issue_media, delete_issue_media_db

from crud.authority_crud import (
    get_all_authorities,
    get_authority,
    create_authority,
    update_authority,
    delete_authority
)

from pymysql.err import IntegrityError

from crud.feature_instance_crud import (
    get_features_for_place,
    add_feature_instance,
    update_feature_instance,
    delete_feature_instance
)


from crud.maintenance_crud import (
    get_maintenance_for_authority,
    assign_task,
    delete_task
)
from crud.feature_instance_crud import get_features_for_place

from crud.feature_crud import (
    get_all_features,
    get_feature,
    create_feature,
    update_feature,
    delete_feature,
)


from crud.issue_crud import (
    get_all_issues,
)

from crud.place_crud import (
    get_all_places,
    get_place,
    create_place,
    update_place,
    delete_place
)

from crud.review_crud import (
    create_or_update_review,
    delete_review,
    get_all_reviews,
    get_review
)

from crud.issue_crud import (
    get_all_issues,
    get_issue,
    create_issue,
    update_issue,
    resolve_issue,
    delete_issue
)

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard-user")
def dashboard_user():
    if session.get("user_role") != "user":
        return redirect("/login")

    return render_template("dashboard_user.html")


@app.route("/dashboard-authority")
def dashboard_authority():
    if session.get("user_role") != "authority":
        return redirect("/login")

    return render_template("dashboard_authority.html")


@app.route("/places")
def places():
    places = get_all_places()
    return render_template("places/list.html", places=places)

@app.route("/places/<int:place_id>/features/add", methods=["GET", "POST"])
def add_place_feature(place_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT feature_id, feature_type FROM Accessibility_Feature ORDER BY feature_type")
    all_features = cur.fetchall()

    cur.execute("SELECT place_id, name FROM Place WHERE place_id=%s", (place_id,))
    place = cur.fetchone()

    cur.close()
    conn.close()

    if request.method == "POST":
        feature_id = request.form["feature_id"]
        status = request.form["status"]

        try:
            add_feature_instance(place_id, feature_id, status)
            flash("Feature added successfully!", "success")
            return redirect(f"/places/{place_id}")

        except IntegrityError:
            flash("⚠️ This place already has this feature type!", "error")
            return redirect(f"/places/{place_id}/features/add")

    return render_template("feature_instance/add.html",
                           place=place,
                           all_features=all_features)



@app.route("/places/add", methods=["GET", "POST"])
def add_place():
    if session.get("user_role") != "authority":
        return redirect("/places") 
    
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "country": request.form["country"],
            "state": request.form["state"],
            "city": request.form["city"],
            "street": request.form["street"],
            "zip_code": request.form["zip_code"],
            "category": request.form["category"],
            "latitude": request.form["latitude"],
            "longitude": request.form["longitude"],
            "verified": 1 if "verified" in request.form else 0,
        }
        create_place(data)
        return redirect("/places")

    return render_template("places/add.html")


@app.route("/places/<int:place_id>")
def place_details(place_id):
    place = get_place(place_id)

    conn = get_connection()
    cur = conn.cursor()

    # Accessibility features
    cur.execute("""
        SELECT 
            af.feature_type,
            af.description,
            fi.status
        FROM Feature_Instance fi
        JOIN Accessibility_Feature af
            ON fi.feature_id = af.feature_id
        WHERE fi.place_id = %s
    """, (place_id,))
    features = cur.fetchall()

    # Reviews + rating (only for logged in users)
    reviews = []
    avg_rating = None

    if session.get("user_role") in ("user", "authority"):
        cur.execute("""
            SELECT r.review_id, r.rating, r.comment,
                   COALESCE(u.first_name, 'Anonymous') AS user_name
            FROM Review r
            LEFT JOIN User u ON r.user_id = u.user_id
            WHERE r.place_id = %s
            ORDER BY r.created_at DESC
        """, (place_id,))
        reviews = cur.fetchall()

    # Average rating for public view
    cur.execute("SELECT AVG(rating) AS avg_rating FROM Review WHERE place_id = %s", (place_id,))
    row = cur.fetchone()
    avg_rating = round(row["avg_rating"], 1) if row["avg_rating"] else None

    cur.close()
    conn.close()

    return render_template(
        "places/details.html",
        place=place,
        features=features,
        reviews=reviews,
        avg_rating=avg_rating
    )


@app.route("/places/edit/<int:place_id>", methods=["GET", "POST"])
def edit_place(place_id):
    place = get_place(place_id)

    if session.get("user_role") != "authority":
        return redirect("/places")


    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "country": request.form["country"],
            "state": request.form["state"],
            "city": request.form["city"],
            "street": request.form["street"],
            "zip_code": request.form["zip_code"],
            "category": request.form["category"],
            "latitude": request.form["latitude"],
            "longitude": request.form["longitude"],
            "verified": 1 if "verified" in request.form else 0,
        }
        update_place(place_id, data)
        return redirect("/places")

    return render_template("places/edit.html", place=place)


@app.route("/places/delete/<int:place_id>")
def delete_place_route(place_id):

    if session.get("user_role") != "authority":
        return redirect("/places")
    
    delete_place(place_id)
    return redirect("/places")


@app.route("/search-places")
def search_places():
    term = request.args.get("q", "")

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT place_id, name, city
        FROM Place
        WHERE name LIKE %s
        ORDER BY name
        LIMIT 10
    """
    cur.execute(query, (term + "%",))
    results = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(results)


@app.route("/reviews")
def reviews():

    place = request.args.get("place")
    rating = request.args.get("rating")
    q = request.args.get("q")

    all_reviews = get_all_reviews(place, rating, q)

    # need to fetch places for filter dropdown
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT place_id, name FROM Place")
    places = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("reviews/list.html", reviews=all_reviews, places=places)


@app.route("/reviews/add", methods=["GET", "POST"])
def add_review():
    if session.get("user_role") != "user":
        return redirect("/login")

    if request.method == "POST":
        user_id = session["user_id"]

        place_id = request.form["place_id"]
        rating = request.form["rating"]
        comment = request.form["comment"]

        # create review first
        review_id = create_or_update_review(user_id, place_id, rating, comment)

        # handle media URL
        media_url = request.form.get("media_url")
        media_type = request.form.get("media_type")

        if media_url:
            add_review_media(review_id, media_url, media_type)

        return redirect("/reviews")

    # -------- GET REQUEST (WHAT YOU MISSED) --------
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT place_id, name FROM Place")
    places = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("reviews/add.html", places=places)


@app.route("/reviews/edit/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    review = get_review(review_id)
    media = get_review_media(review_id)

    if request.method == "POST":
        create_or_update_review(
            review["user_id"],
            review["place_id"],
            request.form["rating"],
            request.form["comment"]
        )

        # add new media if provided
        new_url = request.form.get("new_media_url")
        new_type = request.form.get("new_media_type")

        if new_url and new_type:
            add_review_media(review_id, new_url, new_type)

        return redirect(f"/reviews/{review_id}")

    return render_template("reviews/edit.html", review=review, media=media)


@app.route("/reviews/delete/<int:review_id>")
def delete_review_route(review_id):
    delete_review(review_id)
    return redirect("/reviews")

@app.route("/reviews/media/delete/<int:media_id>")
def delete_review_media_route(media_id):
    delete_review_media(media_id)
    return redirect(request.referrer)


@app.route("/reviews/<int:review_id>")
def review_details(review_id):
    review = get_review(review_id)
    media = get_review_media(review_id)

    return render_template("reviews/details.html", review=review, media=media)


@app.route("/issues")
def issues_list():

    # USER VIEW → only their issues
    if session.get("user_role") == "user":
        user_id = session["user_id"]

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT Issue_Report.*, Place.name AS place_name
            FROM Issue_Report
            JOIN Place ON Issue_Report.place_id = Place.place_id
            WHERE Issue_Report.user_id = %s
            ORDER BY Issue_Report.created_at DESC
        """

        cur.execute(query, (user_id,))
        issues = cur.fetchall()
        cur.close()
        conn.close()

        return render_template("issues/my_list.html", issues=issues)

    # AUTHORITY VIEW → all issues, but without user info
    elif session.get("user_role") == "authority":

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT Issue_Report.*, Place.name AS place_name
            FROM Issue_Report
            JOIN Place ON Issue_Report.place_id = Place.place_id
            ORDER BY Issue_Report.created_at DESC
        """

        cur.execute(query)
        issues = cur.fetchall()
        cur.close()
        conn.close()

        return render_template("issues/list.html", issues=issues)

    # Not logged in
    return redirect("/login")


@app.route("/issues/add", methods=["GET", "POST"])
def add_issue():
    if session.get("user_role") not in ("user", "authority"):
        return redirect("/login")

    if request.method == "POST":
        # Create issue
        report_id = create_issue(
            session["user_id"],
            request.form["place_id"],
            request.form["issue_type"],
            request.form["severity"],
            request.form["description"]
        )

        # If media provided, save it
        media_url = request.form.get("media_url")
        media_type = request.form.get("media_type")

        if media_url:
            add_issue_media(report_id, media_url, media_type)

        return redirect("/issues")

    # Load places for dropdown
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT place_id, name FROM Place")
    places = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("issues/add.html", places=places)



@app.route("/issues/<int:report_id>")
def issue_details(report_id):
    issue = get_issue(report_id)
    media = get_issue_media(report_id)

    return render_template("issues/details.html", issue=issue, media=media)



@app.route("/issues/edit/<int:report_id>", methods=["GET", "POST"])
def edit_issue_route(report_id):
    issue = get_issue(report_id)
    media = get_issue_media(report_id)

    if request.method == "POST":
        update_issue(
            report_id,
            request.form["issue_type"],
            request.form["severity"],
            request.form["status"],
            request.form["description"]
        )

        # If user added new media
        new_url = request.form.get("new_media_url")
        new_type = request.form.get("new_media_type")

        if new_url and new_type:
            add_issue_media(report_id, new_url, new_type)

        return redirect(f"/issues/{report_id}")

    return render_template("issues/edit.html", issue=issue, media=media)

@app.route("/issues/resolve/<int:report_id>")
def resolve_issue_route(report_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    resolve_issue(report_id, session["authority_id"])
    return redirect("/issues")


@app.route("/issues/delete/<int:report_id>")
def delete_issue_route(report_id):
    delete_issue(report_id)
    return redirect("/issues")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]   # "user" or "authority"

        conn = get_connection()
        cur = conn.cursor()

        # ======================================================
        # USER LOGIN
        # ======================================================
        if role == "user":
            cur.execute("SELECT * FROM User WHERE email=%s", (email,))
            user = cur.fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["user_id"]
                session["user_role"] = "user"
                cur.close()
                conn.close()
                return redirect("/dashboard-user")

            flash("Invalid email or password", "error")

        # ======================================================
        # AUTHORITY LOGIN
        # ======================================================
        elif role == "authority":
            cur.execute("SELECT * FROM Authority WHERE email=%s", (email,))
            authority = cur.fetchone()

            if authority and check_password_hash(authority["password_hash"], password):
                session["authority_id"] = authority["authority_id"]
                session["user_role"] = "authority"
                cur.close()
                conn.close()
                return redirect("/dashboard-authority")

            flash("Invalid email or password", "error")

        cur.close()
        conn.close()

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        success = register_user(
            request.form["first_name"],
            request.form["last_name"],
            request.form["email"],
            request.form["password"],
            request.form["disability"]
        )

        if not success:
            flash("User already exists!", "error")
            return redirect("/register")

        flash("Registration successful! Please login.", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route("/issues/my")
def my_issues():
    if session.get("user_role") != "user":
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT Issue_Report.*, Place.name AS place_name
        FROM Issue_Report
        JOIN Place ON Issue_Report.place_id = Place.place_id
        WHERE Issue_Report.user_id = %s
        ORDER BY Issue_Report.created_at DESC
    """

    cur.execute(query, (user_id,))
    issues = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("issues/my_list.html", issues=issues)

@app.route("/features")
def feature_list():
    if session.get("user_role") != "authority":
        return redirect("/login")
    features = get_all_features()
    return render_template("features/list.html", features=features)


@app.route("/authority/places")
def authority_places():
    if session.get("user_role") != "authority":
        return redirect("/login")
    places = get_all_places()
    return render_template("authority/manage_places.html", places=places)

@app.route("/authority/features")
def authority_feature_list():
    return redirect("/features")

@app.route("/maintenance")
def maintenance_dashboard():
    if session.get("user_role") != "authority":
        return redirect("/login")

    authority_id = session["authority_id"]
    tasks = get_maintenance_for_authority(authority_id)

    return render_template("maintenance/list.html", tasks=tasks)

@app.route("/maintenance/assign/<int:place_id>", methods=["GET", "POST"])
def assign_maintenance(place_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    authority_id = session["authority_id"]

    if request.method == "POST":
        try:
            assign_task(
                authority_id,
                place_id,
                request.form["instance_id"],
                request.form["role"]
            )
            flash("Maintenance task assigned successfully!", "success")
            return redirect("/maintenance")

        except IntegrityError:
            flash("⚠️ This maintenance task already exists!", "error")
            return redirect(f"/maintenance/assign/{place_id}")

    # fetch all features at this place
    features = get_features_for_place(place_id)

    return render_template(
        "maintenance/assign.html",
        place_id=place_id,
        features=features
    )


@app.route("/maintenance/delete/<int:place_id>/<int:instance_id>")
def delete_maintenance(place_id, instance_id):
    authority_id = session["authority_id"]
    delete_task(authority_id, place_id, instance_id)
    return redirect("/maintenance")


@app.route("/places/<int:place_id>/features")
def place_feature_list(place_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    place = get_place(place_id)
    features = get_features_for_place(place_id)

    return render_template("feature_instance/list.html", place=place, features=features)

@app.route("/features")
def features_list():
    if session.get("user_role") != "authority":
        return redirect("/login")

    features = get_all_features()
    return render_template("features/list.html", features=features)


@app.route("/features/add", methods=["GET", "POST"])
def add_feature():
    if session.get("user_role") != "authority":
        return redirect("/login")

    if request.method == "POST":
        create_feature(
            request.form["feature_type"],
            request.form["description"]
        )
        return redirect("/features")

    return render_template("features/add.html")


@app.route("/features/edit/<int:feature_id>", methods=["GET", "POST"])
def edit_feature(feature_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    feature = get_feature(feature_id)

    if request.method == "POST":
        update_feature(
            feature_id,
            request.form["feature_type"],
            request.form["description"]
        )
        return redirect("/features")

    return render_template("features/edit.html", feature=feature)


@app.route("/features/delete/<int:feature_id>")
def delete_feature_route(feature_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    delete_feature(feature_id)
    return redirect("/features")



@app.route("/authorities")
def authorities_list():
    if session.get("user_role") != "authority":
        return redirect("/login")

    authorities = get_all_authorities()
    return render_template("authorities/list.html", authorities=authorities)


@app.route("/authorities/add", methods=["GET", "POST"])
def add_authority():
    if session.get("user_role") != "authority":
        return redirect("/login")

    if request.method == "POST":
        success = create_authority(
            request.form["first_name"],
            request.form["last_name"],
            request.form["email"],
            request.form["phone"],
            request.form["password"]
        )

        if not success:
            flash("Authority already exists with this email or phone!", "error")
            return redirect("/authorities/add")

        flash("Authority added successfully!", "success")
        return redirect("/authorities")

    return render_template("authorities/add.html")


@app.route("/authorities/edit/<int:authority_id>", methods=["GET", "POST"])
def edit_authority(authority_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    authority = get_authority(authority_id)

    if request.method == "POST":
        update_authority(
            authority_id,
            request.form["first_name"],
            request.form["last_name"],
            request.form["email"],
            request.form["phone"]
        )
        flash("Authority updated.", "success")
        return redirect("/authorities")

    return render_template("authorities/edit.html", authority=authority)


@app.route("/authorities/delete/<int:authority_id>")
def delete_authority_route(authority_id):
    if session.get("user_role") != "authority":
        return redirect("/login")

    delete_authority(authority_id)
    flash("Authority deleted.", "error")
    return redirect("/authorities")

@app.route("/issues/media/delete/<int:media_id>")
def delete_issue_media(media_id):
    delete_issue_media_db(media_id)
    return redirect(request.referrer)



if __name__ == "__main__":
    app.run(port=5008, debug=True)
