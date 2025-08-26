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

@app.route("/students")
def students():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return render_template("students.html", students=students)

@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        c.execute("UPDATE students SET name=? WHERE id=?", (name, id))
        conn.commit()
        conn.close()
        return redirect(url_for("students"))
    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()
    return render_template("edit_student.html", student=student)

@app.route("/delete_student/<int:id>")
def delete_student(id):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("students"))

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

@app.route("/attendance_records")
def attendance_records():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("""SELECT attendance.id, students.name, courses.name, attendance.status, attendance.date
                 FROM attendance
                 JOIN students ON students.id = attendance.student_id
                 JOIN courses ON courses.id = attendance.course_id
                 ORDER BY attendance.date DESC""")
    records = c.fetchall()
    conn.close()
    return render_template("attendance_records.html", records=records)

@app.route("/edit_attendance/<int:id>", methods=["GET", "POST"])
def edit_attendance(id):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    if request.method == "POST":
        status = request.form["status"]
        date = request.form["date"]
        c.execute("UPDATE attendance SET status=?, date=? WHERE id=?", (status, date, id))
        conn.commit()
        conn.close()
        return redirect(url_for("attendance_records"))
    c.execute("""SELECT attendance.id, students.name, courses.name, attendance.status, attendance.date
                 FROM attendance
                 JOIN students ON students.id = attendance.student_id
                 JOIN courses ON courses.id = attendance.course_id
                 WHERE attendance.id=?""", (id,))
    record = c.fetchone()
    conn.close()
    return render_template("edit_attendance.html", record=record)

@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("attendance_records"))



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

@app.route("/courses")
def courses():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    conn.close()
    return render_template("courses.html", courses=courses)

@app.route("/edit_course/<int:id>", methods=["GET", "POST"])
def edit_course(id):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        c.execute("UPDATE courses SET name=? WHERE id=?", (name, id))
        conn.commit()
        conn.close()
        return redirect(url_for("courses"))
    c.execute("SELECT * FROM courses WHERE id=?", (id,))
    course = c.fetchone()
    conn.close()
    return render_template("edit_course.html", course=course)

@app.route("/delete_course/<int:id>")
def delete_course(id):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("DELETE FROM courses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("courses"))


if __name__ == "__main__":
    app.run(debug=True)
