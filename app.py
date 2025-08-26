from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()

    # Students table
    c.execute("""CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )""")

    # Courses table
    c.execute("""CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )""")

    # Attendance table (linked with course + student)
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    course_id INTEGER,
                    status TEXT,
                    date TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(course_id) REFERENCES courses(id)
                )""")
    conn.commit()
    conn.close()


init_db()

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_student.html")

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    conn.close()

    if request.method == "POST":
        course_id = request.form.get("course")
        today = request.form.get("date")

        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()

        for student in students:
            status = request.form.get(str(student[0]))
            c.execute("INSERT INTO attendance (student_id, course_id, status, date) VALUES (?, ?, ?, ?)",
                      (student[0], course_id, status, today))

        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("attendance.html", students=students, courses=courses)


@app.route("/view_attendance", methods=["GET", "POST"])
def view_attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    conn.close()

    records = []
    if request.method == "POST":
        course_id = request.form.get("course")
        date_selected = request.form.get("date")

        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("""SELECT students.name, attendance.status, attendance.date, courses.name
                     FROM attendance
                     JOIN students ON students.id = attendance.student_id
                     JOIN courses ON courses.id = attendance.course_id
                     WHERE attendance.course_id = ? AND attendance.date = ?""",
                  (course_id, date_selected))
        records = c.fetchall()
        conn.close()

    return render_template("view_attendance.html", courses=courses, records=records)


@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    if request.method == "POST":
        name = request.form["name"]
        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("INSERT INTO courses (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_course.html")


if __name__ == "__main__":
    app.run(debug=True)
