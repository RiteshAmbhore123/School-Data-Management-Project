import os
import csv
import io
from datetime import date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, init_db

CLASSES = list(range(1, 11))
SECTIONS = ["A", "B", "C"]


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SCHOOL_APP_SECRET_KEY", "dev-key-change-me")

    init_db(app)
    register_routes(app)
    return app


# ---------- auth helpers ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


# ---------- routes ----------

def register_routes(app):

    @app.context_processor
    def inject_globals():
        return {"CLASSES": CLASSES, "current_user": get_current_user()}

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            role = request.form.get("role")
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE role = ? AND username = ?", (role, username)
            ).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["role"] = user["role"]
                flash(f"Welcome back, {user['display_name']}.", "success")
                return redirect(url_for("dashboard"))
            flash("Incorrect username or password for this role.", "error")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been signed out.", "success")
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def dashboard():
        db = get_db()
        total_students = db.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]

        per_class = []
        for c in CLASSES:
            count = db.execute(
                "SELECT COUNT(*) AS c FROM students WHERE class_name = ?", (c,)
            ).fetchone()["c"]
            per_class.append({"class_name": c, "count": count})
        classes_in_use = sum(1 for row in per_class if row["count"] > 0)

        today = date.today().isoformat()
        rows = db.execute(
            "SELECT status FROM attendance WHERE date = ?", (today,)
        ).fetchall()
        present_today = sum(1 for r in rows if r["status"] == "present")
        total_marked = len(rows)

        return render_template(
            "dashboard.html",
            total_students=total_students,
            per_class=per_class,
            classes_in_use=classes_in_use,
            present_today=present_today,
            total_marked=total_marked,
            today=today,
        )

    # ---- students ----

    @app.route("/students")
    @login_required
    def students():
        db = get_db()
        class_filter = request.args.get("class", "all")
        q = request.args.get("q", "").strip()

        sql = "SELECT * FROM students WHERE 1=1"
        params = []
        if class_filter != "all":
            sql += " AND class_name = ?"
            params.append(int(class_filter))
        if q:
            sql += " AND (name LIKE ? OR roll_no LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like])
        sql += " ORDER BY class_name, roll_no"

        student_list = db.execute(sql, params).fetchall()
        counts = {
            c: db.execute(
                "SELECT COUNT(*) AS c FROM students WHERE class_name = ?", (c,)
            ).fetchone()["c"]
            for c in CLASSES
        }

        return render_template(
            "students.html",
            students=student_list,
            class_filter=class_filter,
            q=q,
            counts=counts,
        )

    @app.route("/students/add", methods=["GET", "POST"])
    @login_required
    def add_student():
        if request.method == "POST":
            error = save_student_form(None)
            if error:
                flash(error, "error")
            else:
                flash("Student added to the register.", "success")
                return redirect(url_for("students"))
        return render_template("student_form.html", student=None, SECTIONS=SECTIONS)

    @app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
    @login_required
    def edit_student(student_id):
        db = get_db()
        student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if student is None:
            flash("That student record no longer exists.", "error")
            return redirect(url_for("students"))

        if request.method == "POST":
            error = save_student_form(student_id)
            if error:
                flash(error, "error")
            else:
                flash("Student record updated.", "success")
                return redirect(url_for("students"))
        return render_template("student_form.html", student=student, SECTIONS=SECTIONS)

    @app.route("/students/delete/<int:student_id>", methods=["POST"])
    @login_required
    def delete_student(student_id):
        db = get_db()
        db.execute("DELETE FROM students WHERE id = ?", (student_id,))
        db.commit()
        flash("Student removed from the register.", "success")
        return redirect(url_for("students"))

    def save_student_form(student_id):
        db = get_db()
        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        contact = request.form.get("contact", "").strip()
        class_name = int(request.form.get("class_name", 1))

        if not name or not roll_no or not contact:
            return "Name, roll number, and contact number are required."

        dup = db.execute(
            "SELECT id FROM students WHERE class_name = ? AND roll_no = ?", (class_name, roll_no)
        ).fetchone()
        if dup and (student_id is None or dup["id"] != student_id):
            return f"Roll number {roll_no} already exists in Standard {class_name}."

        values = {
            "roll_no": roll_no,
            "name": name,
            "class_name": class_name,
            "section": request.form.get("section", "A"),
            "gender": request.form.get("gender", "Male"),
            "dob": request.form.get("dob", ""),
            "parent_name": request.form.get("parent_name", ""),
            "contact": contact,
            "address": request.form.get("address", ""),
            "admission_date": request.form.get("admission_date") or date.today().isoformat(),
            "blood_group": request.form.get("blood_group", ""),
        }

        if student_id is None:
            db.execute(
                """INSERT INTO students
                   (roll_no, name, class_name, section, gender, dob, parent_name,
                    contact, address, admission_date, blood_group)
                   VALUES (:roll_no, :name, :class_name, :section, :gender, :dob,
                           :parent_name, :contact, :address, :admission_date, :blood_group)""",
                values,
            )
        else:
            values["id"] = student_id
            db.execute(
                """UPDATE students SET
                       roll_no=:roll_no, name=:name, class_name=:class_name, section=:section,
                       gender=:gender, dob=:dob, parent_name=:parent_name, contact=:contact,
                       address=:address, admission_date=:admission_date, blood_group=:blood_group
                   WHERE id=:id""",
                values,
            )
        db.commit()
        return None

    @app.route("/students/export.csv")
    @login_required
    def export_students_csv():
        db = get_db()
        rows = db.execute("SELECT * FROM students ORDER BY class_name, roll_no").fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["Roll No", "Name", "Class", "Section", "Gender", "DOB", "Parent",
             "Contact", "Address", "Admission Date", "Blood Group"]
        )
        for s in rows:
            writer.writerow(
                [s["roll_no"], s["name"], s["class_name"], s["section"], s["gender"], s["dob"],
                 s["parent_name"], s["contact"], s["address"], s["admission_date"], s["blood_group"]]
            )

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=students.csv"},
        )

    # ---- attendance ----

    @app.route("/attendance", methods=["GET", "POST"])
    @login_required
    def attendance():
        db = get_db()
        class_name = int(request.values.get("class_name", 1))
        att_date = request.values.get("date", date.today().isoformat())

        if request.method == "POST":
            class_students = db.execute(
                "SELECT * FROM students WHERE class_name = ?", (class_name,)
            ).fetchall()
            for s in class_students:
                status = request.form.get(f"status_{s['id']}")
                if not status:
                    continue
                existing = db.execute(
                    "SELECT id FROM attendance WHERE student_id = ? AND date = ?",
                    (s["id"], att_date),
                ).fetchone()
                if existing:
                    db.execute(
                        "UPDATE attendance SET status = ? WHERE id = ?", (status, existing["id"])
                    )
                else:
                    db.execute(
                        "INSERT INTO attendance (student_id, class_name, date, status) VALUES (?, ?, ?, ?)",
                        (s["id"], class_name, att_date, status),
                    )
            db.commit()
            flash("Attendance saved.", "success")
            return redirect(url_for("attendance", class_name=class_name, date=att_date))

        class_students = db.execute(
            "SELECT * FROM students WHERE class_name = ? ORDER BY roll_no", (class_name,)
        ).fetchall()
        rows = db.execute(
            "SELECT student_id, status FROM attendance WHERE date = ? AND class_name = ?",
            (att_date, class_name),
        ).fetchall()
        records = {r["student_id"]: r["status"] for r in rows}
        present_count = sum(1 for v in records.values() if v == "present")

        return render_template(
            "attendance.html",
            class_name=class_name,
            att_date=att_date,
            class_students=class_students,
            records=records,
            present_count=present_count,
        )

    # ---- settings ----

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        db = get_db()
        if request.method == "POST":
            role = request.form.get("role")
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            target = db.execute("SELECT * FROM users WHERE role = ?", (role,)).fetchone()
            if not target or not check_password_hash(target["password_hash"], current_pw):
                flash("Current password is incorrect.", "error")
            elif len(new_pw) < 6:
                flash("New password must be at least 6 characters.", "error")
            elif new_pw != confirm_pw:
                flash("New password and confirmation do not match.", "error")
            else:
                db.execute(
                    "UPDATE users SET password_hash = ? WHERE role = ?",
                    (generate_password_hash(new_pw), role),
                )
                db.commit()
                flash(f"Password updated for {target['display_name']}.", "success")

        users = db.execute("SELECT * FROM users").fetchall()
        return render_template("settings.html", users=users)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
