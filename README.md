# School Student Management System (Python / Flask)

A web application for managing student admissions and attendance for
Standard 1 through Standard 10, with a secure login for the Administrator
and the Principal. Data is stored in a real SQLite database file, not in
memory, so it survives restarts.

## Features

- **Secure login** for two roles: Administrator and Principal (passwords
  are hashed with Werkzeug's `generate_password_hash`, never stored in
  plain text).
- **Student records** by class (Standard 1–10): name, roll number, class,
  section, gender, date of birth, parent/guardian name, contact number,
  address, admission date, and blood group.
- **Add / edit / delete** students, with duplicate roll-number checking
  per class.
- **Search and filter** students by name, roll number, or class.
- **Attendance**: mark present/absent per class per day, with a daily
  summary.
- **CSV export** of the student list.
- **Change password** for either account from the Settings page.
- **Dashboard** with enrolment totals and a students-per-class chart.

## Requirements

- Python 3.9+
- Flask (the only external dependency — everything else, including the
  database layer, uses Python's built-in `sqlite3` module)

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

The app starts at `http://127.0.0.1:5000`. On first run it automatically
creates `instance/school.db` and seeds two accounts:

| Role          | Username    | Password       |
|---------------|-------------|----------------|
| Administrator | `admin`     | `admin@123`    |
| Principal     | `principal` | `principal@123`|

**Change both passwords from the Settings page as soon as you sign in.**

## Project structure

```
school_management/
├── app.py                # Flask routes and application logic
├── db.py                 # SQLite connection handling and seeding
├── schema.sql             # Database table definitions
├── requirements.txt
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── student_form.html
│   ├── attendance.html
│   └── settings.html
├── static/
│   └── style.css          # All styling
└── instance/
    └── school.db           # Created automatically on first run
```

## Notes on security and deploying for real use

- This app is ready for trusted, internal school use out of the box.
- Before exposing it beyond your own machine:
  - Set a strong, random `SCHOOL_APP_SECRET_KEY` environment variable
    (used to sign session cookies) instead of the built-in development key.
  - Run it behind HTTPS (e.g. with a reverse proxy such as Nginx) and a
    production WSGI server (e.g. `gunicorn app:app`), not Flask's
    built-in development server.
  - Consider moving from SQLite to a managed database like PostgreSQL if
    multiple people will use it concurrently at scale.
