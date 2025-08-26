from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    status TEXT,
                    date TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id)
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
    conn.close()

    if request.method == "POST":
        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        today = str(date.today())

        for student in students:
            status = request.form.get(str(student[0]))
            c.execute("INSERT INTO attendance (student_id, status, date) VALUES (?, ?, ?)",
                      (student[0], status, today))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("attendance.html", students=students)

@app.route("/view_attendance")
def view_attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("""SELECT students.name, attendance.status, attendance.date
                 FROM attendance
                 JOIN students ON students.id = attendance.student_id
                 ORDER BY attendance.date DESC""")
    records = c.fetchall()
    conn.close()
    return render_template("view_attendance.html", records=records)

if __name__ == "__main__":
    app.run(debug=True)
