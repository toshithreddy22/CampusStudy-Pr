from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import openai

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-campus-secret-key")
DATABASE = os.path.join(os.path.dirname(__file__), "campus.db")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

COMMON_FIRST_YEAR_SUBJECTS = [
    "Engineering Mathematics",
    "Engineering Physics",
    "Engineering Chemistry",
    "Basic Electrical Engineering",
    "Basic Electronics",
    "Engineering Graphics / Drawing",
    "Programming in C / Python",
    "Communication Skills / English",
    "Engineering Mechanics",
    "Environmental Science",
]

RECOMMENDED_BOOKS = [
    {"subject": "Engineering Mathematics", "title": "Higher Engineering Mathematics", "author": "B.S. Grewal"},
    {"subject": "Engineering Physics", "title": "Engineering Physics", "author": "H.K. Malik & A.K. Singh"},
    {"subject": "Engineering Chemistry", "title": "Engineering Chemistry", "author": "Jain & Jain"},
    {"subject": "Programming in C", "title": "Programming in ANSI C", "author": "E. Balagurusamy"},
    {"subject": "Engineering Drawing", "title": "Engineering Drawing", "author": "N.D. Bhatt"},
    {"subject": "Basic Electrical Engineering", "title": "Electrical Technology", "author": "B.L. Theraja"},
    {"subject": "Engineering Mechanics", "title": "Engineering Mechanics", "author": "F.P. Beer & Johnston"},
    {"subject": "Data Structures", "title": "Data Structures Using C", "author": "Reema Thareja"},
    {"subject": "Digital Electronics", "title": "Digital Principles", "author": "Morris Mano"},
]

BRANCH_BOOKS = {
    "CSE": [
        {"title": "Data Structures", "author": "Seymour Lipschutz"},
        {"title": "DBMS", "author": "Korth"},
        {"title": "Operating Systems", "author": "Galvin"},
        {"title": "Computer Networks", "author": "Forouzan"},
        {"title": "Machine Learning", "author": "Tom M. Mitchell"},
        {"title": "Compiler Design", "author": "Aho, Sethi & Ullman"},
    ],
    "ME": [
        {"title": "Thermodynamics", "author": "P.K. Nag"},
        {"title": "Fluid Mechanics", "author": "R.K. Bansal"},
        {"title": "Theory of Machines", "author": "R.S. Khurmi"},
        {"title": "Strength of Materials", "author": "R.K. Rajput"},
    ],
    "CE": [
        {"title": "Surveying", "author": "B.C. Punmia"},
        {"title": "Structural Analysis", "author": "Hibbeler"},
        {"title": "RCC Design", "author": "Pillai & Menon"},
        {"title": "Soil Mechanics", "author": "B.M. Das"},
    ],
    "EEE": [
        {"title": "Circuit Theory", "author": "Van Valkenburg"},
        {"title": "Power Systems", "author": "C.L. Wadhwa"},
        {"title": "Control Systems", "author": "N. K. Sinha"},
        {"title": "Electrical Machines", "author": "P.S. Bimbhra"},
    ],
    "ECE": [
        {"title": "Analog Electronics", "author": "Boylestad"},
        {"title": "Digital Electronics", "author": "Morris Mano"},
        {"title": "Signals & Systems", "author": "Oppenheim"},
        {"title": "Microprocessors", "author": "Ramesh S. Gaonkar"},
    ],
}

HELPFUL_RESOURCES = [
    {
        "title": "Complete B.Tech First Year Playlist",
        "url": "https://www.youtube.com/results?search_query=btech+first+year+engineering+subjects",
    },
]


def get_chatgpt_response(question):
    if not question or not question.strip():
        return "Please type your doubt clearly so the ChatGPT assistant can help with your B.Tech topic."

    if not OPENAI_API_KEY:
        return (
            "ChatGPT is not configured yet. Set the OPENAI_API_KEY environment variable before using this feature."
        )

    prompt = (
        "You are a helpful study assistant for B.Tech students. "
        "Answer this doubt clearly, provide study advice, and mention relevant books or resources when appropriate. "
        f"Student doubt: {question}"
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and friendly assistant for engineering students preparing for B.Tech courses."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=450,
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        return f"ChatGPT request failed: {str(exc)}"


def get_ai_answer(question):
    if OPENAI_API_KEY:
        return get_chatgpt_response(question)

    question_text = (question or "").strip()
    if not question_text:
        return "Please type your doubt clearly so the AI Boot can help with a subject, book, or study strategy."

    q = question_text.lower()
    if any(term in q for term in ["prepare", "study", "revision", "exam", "score", "read"]):
        return (
            "Focus on understanding the fundamentals first, then solve practice questions. "
            "For theory subjects, summarize each chapter in your own words. For calculation-based subjects, "
            "practice problems daily and review mistakes."
        )

    if any(term in q for term in ["math", "mathematics", "calculus", "algebra", "matrix"]):
        return (
            "Engineering Mathematics is best learned by doing problems. "
            "Use a reliable text like B.S. Grewal, revise formulas, and solve previous year questions to build speed and confidence."
        )

    if any(term in q for term in ["physics", "engineering physics", "optics", "mechanics"]):
        return (
            "For Engineering Physics, focus on conceptual clarity and diagrams. "
            "Practice numerical problems from each chapter and review the derivations step-by-step."
        )

    if any(term in q for term in ["chemistry", "engineering chemistry", "organic", "inorganic"]):
        return (
            "Engineering Chemistry is about concepts and application. "
            "Make short notes for reactions, practice numerical problems, and memorize key concepts using flashcards."
        )

    if any(term in q for term in ["programming", "c programming", "python", "coding", "data structure"]):
        return (
            "Programming questions are solved by writing and running code. "
            "Start with basic syntax and practice small programs. For data structures, understand how each structure works and implement it manually."
        )

    if any(term in q for term in ["drawing", "graphics", "engineering drawing", "drafting"]):
        return (
            "Engineering Drawing improves with practice. "
            "Draw each shape carefully, keep dimensions neat, and review projection rules regularly. Use reference problems from N.D. Bhatt."
        )

    if any(term in q for term in ["electrical", "electronics", "circuit", "system", "control"]):
        return (
            "Electrical and Electronics topics need both theory and solved examples. "
            "Understand the circuit behavior, then solve example problems to see how formulas are applied."
        )

    if any(term in q for term in ["book", "recommend", "textbook", "reference"]):
        return (
            "I recommend standard books like Grewal for Math, Malik for Physics, Jain & Jain for Chemistry, "
            "Balagurusamy for C programming, Bhatt for Engineering Drawing, and Morris Mano for Digital Electronics."
        )

    return (
        "AI Boot is ready to help. Ask about any B.Tech subject, a textbook recommendation, exam preparation, or a doubt you want to solve. "
        "If your question mentions a subject or a chapter, the answer will be more precise."
    )


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            year TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            published_on TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            course TEXT NOT NULL,
            branch TEXT NOT NULL,
            semester TEXT NOT NULL,
            edition TEXT
        )
        """
    )
    conn.commit()

    existing_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if existing_books == 0:
        default_books = [
            ("Higher Engineering Mathematics", "B.S. Grewal", "Engineering Mathematics", "All", "1st Semester", "40th"),
            ("Engineering Physics", "H.K. Malik & A.K. Singh", "Engineering Physics", "All", "1st Semester", "1st"),
            ("Engineering Chemistry", "Jain & Jain", "Engineering Chemistry", "All", "1st Semester", "1st"),
            ("Programming in ANSI C", "E. Balagurusamy", "Programming in C", "All", "1st Semester", "8th"),
            ("Engineering Drawing", "N.D. Bhatt", "Engineering Graphics", "All", "1st Semester", "53rd"),
            ("Electrical Technology", "B.L. Theraja", "Basic Electrical Engineering", "All", "1st Semester", "36th"),
            ("Engineering Mechanics", "F.P. Beer & Johnston", "Engineering Mechanics", "All", "2nd Semester", "8th"),
            ("Data Structures Using C", "Reema Thareja", "Data Structures", "CSE", "4th Semester", "3rd"),
            ("Digital Principles", "Morris Mano", "Digital Electronics", "ECE", "3rd Semester", "12th"),
            ("DBMS", "Korth", "DBMS", "CSE", "5th Semester", "3rd"),
            ("Operating Systems", "Galvin", "Operating Systems", "CSE", "6th Semester", "10th"),
            ("Computer Networks", "Forouzan", "Computer Networks", "CSE", "7th Semester", "6th"),
            ("Thermodynamics", "P.K. Nag", "Thermodynamics", "ME", "3rd Semester", "7th"),
            ("Fluid Mechanics", "R.K. Bansal", "Fluid Mechanics", "CE", "4th Semester", "6th"),
            ("Strength of Materials", "R.K. Rajput", "Strength of Materials", "ME", "4th Semester", "5th"),
            ("Surveying", "B.C. Punmia", "Surveying", "CE", "5th Semester", "48th"),
            ("Structural Analysis", "Hibbeler", "Structural Analysis", "CE", "7th Semester", "4th"),
            ("RCC Design", "Pillai & Menon", "RCC Design", "CE", "6th Semester", "25th"),
            ("Soil Mechanics", "B.M. Das", "Soil Mechanics", "CE", "6th Semester", "12th"),
            ("Power Systems", "C.L. Wadhwa", "Power Systems", "EEE", "7th Semester", "5th"),
            ("Electrical Machines", "P.S. Bimbhra", "Electrical Machines", "EEE", "6th Semester", "5th"),
            ("Network Analysis", "Van Valkenburg", "Circuit Theory", "EEE", "3rd Semester", "3rd"),
            ("Electronic Devices", "Boylestad", "Analog Electronics", "ECE", "5th Semester", "12th"),
            ("Signals & Systems", "Oppenheim", "Signals & Systems", "ECE", "5th Semester", "3rd"),
            ("Microprocessors", "Ramesh S. Gaonkar", "Microprocessors", "ECE", "7th Semester", "1st"),
            ("Java: The Complete Reference", "Herbert Schildt", "Programming", "CSE", "2nd Semester", "11th"),
            ("Structural Analysis", "Hibbeler", "Structural Analysis", "CE", "7th Semester", "4th"),
        ]
        cur.executemany(
            "INSERT INTO books (title, author, course, branch, semester, edition) VALUES (?, ?, ?, ?, ?, ?)",
            default_books,
        )
        conn.commit()

    conn.close()


@app.route("/")
def index():
    conn = get_db_connection()
    stats = {
        "students": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "attendance": conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0],
        "assignments": conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0],
        "notices": conn.execute("SELECT COUNT(*) FROM notices").fetchone()[0],
        "books": conn.execute("SELECT COUNT(*) FROM books").fetchone()[0],
    }
    recent_assignments = conn.execute(
        "SELECT title, due_date FROM assignments ORDER BY due_date ASC LIMIT 4"
    ).fetchall()
    recent_notices = conn.execute(
        "SELECT title, published_on FROM notices ORDER BY published_on DESC LIMIT 4"
    ).fetchall()
    recent_attendance = conn.execute(
        "SELECT s.name, a.status, a.date FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.date DESC LIMIT 4"
    ).fetchall()
    conn.close()
    return render_template(
        "index.html",
        stats=stats,
        recent_assignments=recent_assignments,
        recent_notices=recent_notices,
        recent_attendance=recent_attendance,
    )


@app.route("/students", methods=["GET", "POST"])
def students():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"].strip()
        student_id = request.form["student_id"].strip()
        department = request.form["department"].strip()
        year = request.form["year"].strip()
        if name and student_id and department and year:
            try:
                conn.execute(
                    "INSERT INTO students (name, student_id, department, year) VALUES (?, ?, ?, ?)",
                    (name, student_id, department, year),
                )
                conn.commit()
                flash("Student record added successfully.", "success")
            except sqlite3.IntegrityError:
                flash("Student ID already exists. Use a unique ID.", "error")
        else:
            flash("All student fields are required.", "error")
        return redirect(url_for("students"))

    student_rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    conn.close()
    return render_template("students.html", students=student_rows)


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    flash("Student record deleted.", "success")
    return redirect(url_for("students"))


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    if request.method == "POST":
        student_id = request.form.get("student_id")
        status = request.form.get("status")
        date = request.form.get("date")
        if student_id and status and date:
            conn.execute(
                "INSERT INTO attendance (student_id, status, date) VALUES (?, ?, ?)",
                (student_id, status, date),
            )
            conn.commit()
            flash("Attendance saved successfully.", "success")
        else:
            flash("Please select a student, status, and date.", "error")
        return redirect(url_for("attendance"))

    attendance_rows = conn.execute(
        "SELECT a.id, s.name, s.student_id as reg_no, a.status, a.date FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.date DESC"
    ).fetchall()
    conn.close()
    return render_template("attendance.html", students=students, attendance=attendance_rows)


@app.route("/attendance/delete/<int:attendance_id>", methods=["POST"])
def delete_attendance(attendance_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    conn.commit()
    conn.close()
    flash("Attendance entry removed.", "success")
    return redirect(url_for("attendance"))


@app.route("/assignments", methods=["GET", "POST"])
def assignments():
    conn = get_db_connection()
    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        due_date = request.form["due_date"].strip()
        if title and description and due_date:
            conn.execute(
                "INSERT INTO assignments (title, description, due_date) VALUES (?, ?, ?)",
                (title, description, due_date),
            )
            conn.commit()
            flash("Assignment posted successfully.", "success")
        else:
            flash("All assignment fields are required.", "error")
        return redirect(url_for("assignments"))

    assignment_rows = conn.execute("SELECT * FROM assignments ORDER BY due_date").fetchall()
    conn.close()
    return render_template("assignments.html", assignments=assignment_rows)


@app.route("/assignments/delete/<int:assignment_id>", methods=["POST"])
def delete_assignment(assignment_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    conn.commit()
    conn.close()
    flash("Assignment deleted.", "success")
    return redirect(url_for("assignments"))


@app.route("/notices", methods=["GET", "POST"])
def notices():
    conn = get_db_connection()
    if request.method == "POST":
        title = request.form["title"].strip()
        message = request.form["message"].strip()
        published_on = request.form["published_on"].strip()
        if title and message and published_on:
            conn.execute(
                "INSERT INTO notices (title, message, published_on) VALUES (?, ?, ?)",
                (title, message, published_on),
            )
            conn.commit()
            flash("Notice posted to the board.", "success")
        else:
            flash("All notice fields are required.", "error")
        return redirect(url_for("notices"))

    notice_rows = conn.execute("SELECT * FROM notices ORDER BY published_on DESC").fetchall()
    conn.close()
    return render_template("notices.html", notices=notice_rows)


@app.route("/notices/delete/<int:notice_id>", methods=["POST"])
def delete_notice(notice_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    conn.commit()
    conn.close()
    flash("Notice removed from the board.", "success")
    return redirect(url_for("notices"))


@app.route("/library", methods=["GET", "POST"])
def library():
    conn = get_db_connection()
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        course = request.form["course"].strip()
        branch = request.form["branch"].strip()
        semester = request.form["semester"].strip()
        edition = request.form.get("edition", "").strip()
        if title and author and course and branch and semester:
            conn.execute(
                "INSERT INTO books (title, author, course, branch, semester, edition) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, course, branch, semester, edition),
            )
            conn.commit()
            flash("Book added to library.", "success")
        else:
            flash("All book fields are required.", "error")
        return redirect(url_for("library"))

    book_rows = conn.execute("SELECT * FROM books ORDER BY branch, semester, course, title").fetchall()
    conn.close()
    return render_template(
        "library.html",
        books=book_rows,
        subjects=COMMON_FIRST_YEAR_SUBJECTS,
        recommended_books=RECOMMENDED_BOOKS,
        branch_books=BRANCH_BOOKS,
        resources=HELPFUL_RESOURCES,
    )


@app.route("/library/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    flash("Book removed from the library.", "success")
    return redirect(url_for("library"))


@app.route("/doubts", methods=["GET", "POST"])
def doubts():
    question = ""
    answer = None
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        answer = get_ai_answer(question)
    return render_template("doubts.html", question=question, answer=answer)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
