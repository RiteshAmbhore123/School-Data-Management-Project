import os
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "school.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db():
    """Return a request-scoped sqlite3 connection with row access by column name."""
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create tables (if missing) and register the connection teardown."""
    with app.app_context():
        db = get_db()
        with open(SCHEMA_PATH, "r") as f:
            db.executescript(f.read())
        db.commit()
        seed_default_users(db)
    app.teardown_appcontext(close_db)


def seed_default_users(db):
    """Create the two built-in accounts the first time the app runs."""
    admin = db.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
    if admin is None:
        db.execute(
            "INSERT INTO users (username, password_hash, role, display_name) VALUES (?, ?, ?, ?)",
            ("admin", generate_password_hash("admin@123"), "admin", "Administrator"),
        )

    principal = db.execute("SELECT id FROM users WHERE role = 'principal'").fetchone()
    if principal is None:
        db.execute(
            "INSERT INTO users (username, password_hash, role, display_name) VALUES (?, ?, ?, ?)",
            ("principal", generate_password_hash("principal@123"), "principal", "Principal"),
        )
    db.commit()
