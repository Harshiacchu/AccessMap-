# AccessMapPlus

### A Web Application for Accessibility Mapping, Issue Reporting, and Authority Management

AccessMapPlus is a Flask-based application that enables users to locate accessible places, report accessibility issues, submit reviews with media, and allow authorities to manage places, features, and maintenance responsibilities.

This project contains a complete implementation of all CRUD operations across the database schema, user and authority authentication, issue tracking, review and media handling, and accessibility feature management.

---

## 1. Features Overview

### User Features

* Register and log in as a user
* Search and view places
* Submit reviews with optional images or videos
* Report accessibility issues with media support
* View and edit previously reported issues
* View all submitted reviews

### Authority Features

* Log in as an authority (no sign-up page; authorities are added by an existing authority)
* Manage places, accessibility features, and feature instances
* Assign maintenance tasks for specific features
* View all reported issues and update their statuses
* Send issue reports via email
* Manage authority accounts (add, edit, delete)

---

## 2. Project Structure

```
AccessMapPlus/
│
├── app.py
├── config.py
├── db.py
│
├── crud/
│   ├── user_crud.py
│   ├── authority_crud.py
│   ├── place_crud.py
│   ├── feature_crud.py
│   ├── feature_instance_crud.py
│   ├── maintenance_crud.py
│   ├── review_crud.py
│   ├── review_media_crud.py
│   ├── issue_crud.py
│   ├── issue_media_crud.py
│
├── templates/
│   ├── layout.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard_user.html
│   ├── dashboard_authority.html
│   ├── ... (places, reviews, issues, features, authorities views)
│
├── static/
│   ├── styles.css
│   ├── glass.css
│   ├── uploads/
│       ├── reviews/
│       ├── issues/

```

---

## 3. Database Setup

Run the provided SQL schema file to create all required tables:

```
mysql -u root -p < schema.sql
```

Ensure that MySQL is running and accessible.

---

## 4. Configuration Instructions (Important)

Before running the application, you must configure `config.py` with your own database credentials and SMTP settings.

### Edit the following fields in `config.py`:

```
DB_HOST = "localhost"
DB_USER = "your_mysql_username"
DB_PASSWORD = "your_mysql_password"
DB_NAME = "AccessMapPlus"

SECRET_KEY = "your_flask_secret_key"

```

---

## 5. Installing Dependencies

Install all required Python packages:

```
pip install flask pymysql werkzeug
```

---

## 6. Running the Application

Start the Flask server:

```
python app.py
```

Then open the application in your browser:

```
http://localhost:5008
```

---

## 7. Authority Login and Setup

Authorities cannot sign up through the UI.
Insert authority accounts directly into the database using SQL:

```
INSERT INTO Authority (first_name, last_name, email, phone, password_hash)
VALUES ('H', 'S', 'h@g.com', '9876543210',
'$2b$12$Ba7xtnX7wr0cbHNBbc26c2857b5d...');
```

Replace with your actual hashed password.

But the first Authority, only needs to be added like this, a registered authority can act as an admin and can add users.

---

## 8. Media Handling

### Review media

Stored via URLs in the `Review_Media` table.
Displayed in review details and edit pages.

### Issue media

Stored in the `Issue_Media` table using URLs provided by the user.

---

## 9. Maintenance Workflow

Authorities can:

1. View all places and their accessibility features
2. Assign maintenance tasks for specific feature instances
3. View their assigned tasks under the Maintenance dashboard
4. Remove tasks as needed

---

## 10. Error Handling and Alerts

The application uses Flask `flash()` alerts for:

* Invalid login
* Duplicate entries
* Missing records
* Successful operations

All alerts appear in the UI using the project's glass-style components.

---

## 11. Authors

* **Harshitha Seetharaman**
* **Muskan Jain**

Khoury College of Computer Sciences
Northeastern University

---
