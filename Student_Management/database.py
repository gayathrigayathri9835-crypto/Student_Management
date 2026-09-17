"""
Student Management System - Database Layer
Handles SQLite database connection, schema creation, data access,
validation, and automated calculation of grades, attendance, and academic status.
"""

import os
import sqlite3
import re
from datetime import datetime

# Database directory and file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "student_management.db")


def get_db_connection():
    """Establish connection to SQLite database with row factory for dict-like access."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def calculate_grade(total):
    """
    Calculate letter grade dynamically based on total mark (out of 100).
    90–100 -> A+
    80–89  -> A
    70–79  -> B+
    60–69  -> B
    50–59  -> C
    Below 50 -> F
    """
    try:
        val = float(total)
    except (ValueError, TypeError):
        return "F"
    if val >= 90:
        return "A+"
    elif val >= 80:
        return "A"
    elif val >= 70:
        return "B+"
    elif val >= 60:
        return "B"
    elif val >= 50:
        return "C"
    else:
        return "F"


def calculate_student_status(attendance_percentage, avg_mark, failed_subjects_count):
    """
    Automatically determine academic status indicator:
    - At Risk: Attendance < 60% AND has failed subjects
    - Needs Attention: Attendance < 75% OR average mark < 60
    - Excellent: Average mark >= 75 AND attendance >= 75%
    - Good: Otherwise with satisfactory metrics
    """
    att = float(attendance_percentage or 0)
    avg = float(avg_mark or 0)
    failed = int(failed_subjects_count or 0)

    if att < 60 and failed > 0:
        return "At Risk"
    elif att < 75 or avg < 60:
        return "Needs Attention"
    elif avg >= 75 and att >= 75:
        return "Excellent"
    else:
        return "Good"


def validate_student_data(data, is_update=False, current_id=None):
    """
    Validate student form data.
    Returns (is_valid, error_message).
    """
    name = (data.get("name") or "").strip()
    reg_no = (data.get("register_number") or "").strip().upper()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    gender = (data.get("gender") or "").strip()
    dob = (data.get("dob") or "").strip()
    dept_id = data.get("department_id")
    course_id = data.get("course_id")
    year = data.get("year")
    section = (data.get("section") or "").strip().upper()
    admission_year = data.get("admission_year")
    address = (data.get("address") or "").strip()

    # Required fields check
    if not all([name, reg_no, email, phone, gender, dob, dept_id, course_id, year, section, admission_year, address]):
        return False, "All fields are required. Please fill in all details."

    # Validate Email Format
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return False, "Please enter a valid email address."

    # Validate Phone Number (must have 10 digits)
    clean_phone = re.sub(r"[\s\-\(\)\+]", "", phone)
    if not (clean_phone.isdigit() and len(clean_phone) in (10, 11, 12)):
        return False, "Phone number must contain at least 10 valid digits."

    # Validate Year
    try:
        y = int(year)
        if y < 1 or y > 5:
            return False, "Academic year must be between 1 and 5."
    except (ValueError, TypeError):
        return False, "Invalid academic year value."

    # Validate Admission Year
    try:
        ay = int(admission_year)
        curr_year = datetime.now().year
        if ay < 2010 or ay > curr_year + 1:
            return False, f"Admission year must be between 2010 and {curr_year + 1}."
    except (ValueError, TypeError):
        return False, "Invalid admission year value."

    # Check for Duplicate Register Number
    conn = get_db_connection()
    try:
        if is_update and current_id:
            existing = conn.execute(
                "SELECT id FROM students WHERE register_number = ? AND id != ?",
                (reg_no, current_id)
            ).fetchone()
        else:
            existing = conn.execute(
                "SELECT id FROM students WHERE register_number = ?",
                (reg_no,)
            ).fetchone()

        if existing:
            return False, f"Register number '{reg_no}' is already assigned to another student."
    finally:
        conn.close()

    return True, None


def init_database_schema():
    """Create all SQLite tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            hod TEXT NOT NULL
        )
    """)

    # 2. Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            department_id INTEGER NOT NULL,
            duration TEXT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
        )
    """)

    # 3. Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            register_number TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL,
            admission_year INTEGER NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE RESTRICT
        )
    """)

    # 4. Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            total_classes INTEGER NOT NULL DEFAULT 0,
            present INTEGER NOT NULL DEFAULT 0,
            absent INTEGER NOT NULL DEFAULT 0,
            percentage REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # 5. Marks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            internal_mark REAL NOT NULL,
            external_mark REAL NOT NULL,
            total REAL NOT NULL,
            grade TEXT NOT NULL,
            UNIQUE(student_id, subject),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # 6. Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def generate_system_alerts():
    """
    Inspect attendance, marks, and student profiles to refresh system alerts dynamically.
    Generates alerts for:
    - Attendance below 75% (Warning) or below 60% (Critical)
    - Failed subjects (Critical)
    - Overall low performance (Warning)
    - Incomplete contact/profile information (Information)
    """
    conn = get_db_connection()
    try:
        # Clear existing automated active alerts
        conn.execute("DELETE FROM alerts WHERE status = 'Active'")

        # 1. Low attendance alerts
        att_records = conn.execute("""
            SELECT a.student_id, a.percentage, s.name, s.register_number
            FROM attendance a
            JOIN students s ON s.id = a.student_id
            WHERE a.percentage < 75
        """).fetchall()

        for r in att_records:
            pct = r["percentage"]
            if pct < 60:
                conn.execute("""
                    INSERT INTO alerts (student_id, alert_type, message, severity, status)
                    VALUES (?, 'Attendance', ?, 'Critical', 'Active')
                """, (r["student_id"], f"Critical attendance shortage ({pct:.1f}%) for {r['name']} ({r['register_number']})."))
            else:
                conn.execute("""
                    INSERT INTO alerts (student_id, alert_type, message, severity, status)
                    VALUES (?, 'Attendance', ?, 'Warning', 'Active')
                """, (r["student_id"], f"Attendance ({pct:.1f}%) is below institutional threshold (75%) for {r['name']}."))

        # 2. Failed subjects alerts
        failed_records = conn.execute("""
            SELECT m.student_id, m.subject, m.total, s.name, s.register_number
            FROM marks m
            JOIN students s ON s.id = m.student_id
            WHERE m.grade = 'F'
        """).fetchall()

        for f in failed_records:
            conn.execute("""
                INSERT INTO alerts (student_id, alert_type, message, severity, status)
                VALUES (?, 'Academic', ?, 'Critical', 'Active')
            """, (f["student_id"], f"Student {f['name']} ({f['register_number']}) failed in {f['subject']} (Total: {f['total']:.1f})."))

        # 3. Overall low performance (average mark < 55)
        avg_low_records = conn.execute("""
            SELECT s.id, s.name, s.register_number, AVG(m.total) as avg_mark
            FROM students s
            JOIN marks m ON m.student_id = s.id
            GROUP BY s.id
            HAVING avg_mark < 55
        """).fetchall()

        for al in avg_low_records:
            conn.execute("""
                INSERT INTO alerts (student_id, alert_type, message, severity, status)
                VALUES (?, 'Performance', ?, 'Warning', 'Active')
            """, (al["id"], f"Low academic performance: Average score of {al['avg_mark']:.1f}% for {al['name']}."))

        conn.commit()
    finally:
        conn.close()


# ==========================================
# Student CRUD & Retrieval Operations
# ==========================================

def get_all_students(search=None, dept_filter=None, year_filter=None, section_filter=None, status_filter=None):
    """Retrieve all students with department & course names, attendance %, and calculated status."""
    conn = get_db_connection()
    query = """
        SELECT
            s.*,
            d.name as department_name,
            d.code as department_code,
            c.name as course_name,
            c.code as course_code,
            COALESCE(a.percentage, 0.0) as attendance_percentage,
            COALESCE(a.total_classes, 0) as total_classes,
            COALESCE(a.present, 0) as present_classes,
            COALESCE(a.absent, 0) as absent_classes,
            ROUND(COALESCE(AVG(m.total), 0), 1) as average_mark,
            SUM(CASE WHEN m.grade = 'F' THEN 1 ELSE 0 END) as failed_subjects
        FROM students s
        LEFT JOIN departments d ON s.department_id = d.id
        LEFT JOIN courses c ON s.course_id = c.id
        LEFT JOIN attendance a ON s.id = a.student_id
        LEFT JOIN marks m ON s.id = m.student_id
        WHERE 1=1
    """
    params = []

    if search:
        s_term = f"%{search.strip()}%"
        query += """
            AND (s.name LIKE ? OR s.register_number LIKE ? OR d.name LIKE ? OR d.code LIKE ? OR c.name LIKE ?)
        """
        params.extend([s_term, s_term, s_term, s_term, s_term])

    if dept_filter and dept_filter != "all":
        query += " AND s.department_id = ?"
        params.append(dept_filter)

    if year_filter and year_filter != "all":
        query += " AND s.year = ?"
        params.append(year_filter)

    if section_filter and section_filter != "all":
        query += " AND s.section = ?"
        params.append(section_filter)

    query += " GROUP BY s.id ORDER BY s.name ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    students = []
    for r in rows:
        item = dict(r)
        # Calculate dynamic status
        status = calculate_student_status(
            item["attendance_percentage"],
            item["average_mark"],
            item["failed_subjects"]
        )
        item["status"] = status
        # Apply status filter in Python if specified
        if status_filter and status_filter != "all" and status != status_filter:
            continue
        students.append(item)

    return students


def get_student_by_id(student_id):
    """Retrieve full student record with joined department, course, attendance, and calculated status."""
    conn = get_db_connection()
    row = conn.execute("""
        SELECT
            s.*,
            d.name as department_name,
            d.code as department_code,
            c.name as course_name,
            c.code as course_code,
            COALESCE(a.percentage, 0.0) as attendance_percentage,
            COALESCE(a.total_classes, 0) as total_classes,
            COALESCE(a.present, 0) as present_classes,
            COALESCE(a.absent, 0) as absent_classes,
            ROUND(COALESCE(AVG(m.total), 0), 1) as average_mark,
            SUM(CASE WHEN m.grade = 'F' THEN 1 ELSE 0 END) as failed_subjects
        FROM students s
        LEFT JOIN departments d ON s.department_id = d.id
        LEFT JOIN courses c ON s.course_id = c.id
        LEFT JOIN attendance a ON s.id = a.student_id
        LEFT JOIN marks m ON s.id = m.student_id
        WHERE s.id = ?
        GROUP BY s.id
    """, (student_id,)).fetchone()
    conn.close()

    if not row:
        return None

    student = dict(row)
    student["status"] = calculate_student_status(
        student["attendance_percentage"],
        student["average_mark"],
        student["failed_subjects"]
    )
    # Overall grade based on average mark
    student["overall_grade"] = calculate_grade(student["average_mark"])
    return student


def add_student(data):
    """Insert a new student and initialize an attendance record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO students (
                name, register_number, email, phone, gender, dob,
                department_id, course_id, year, section, admission_year, address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"].strip(),
            data["register_number"].strip().upper(),
            data["email"].strip().lower(),
            data["phone"].strip(),
            data["gender"].strip(),
            data["dob"].strip(),
            int(data["department_id"]),
            int(data["course_id"]),
            int(data["year"]),
            data["section"].strip().upper(),
            int(data["admission_year"]),
            data["address"].strip()
        ))
        new_id = cursor.lastrowid

        # Automatically initialize attendance record for new student
        total_cls = int(data.get("total_classes", 60))
        present_cls = int(data.get("present", 55))
        absent_cls = max(0, total_cls - present_cls)
        pct = round((present_cls / total_cls) * 100, 2) if total_cls > 0 else 0.0

        cursor.execute("""
            INSERT INTO attendance (student_id, total_classes, present, absent, percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (new_id, total_cls, present_cls, absent_cls, pct))

        conn.commit()
    finally:
        conn.close()

    generate_system_alerts()
    return new_id


def update_student(student_id, data):
    """Update existing student details."""
    conn = get_db_connection()
    try:
        conn.execute("""
            UPDATE students SET
                name = ?,
                email = ?,
                phone = ?,
                gender = ?,
                dob = ?,
                department_id = ?,
                course_id = ?,
                year = ?,
                section = ?,
                admission_year = ?,
                address = ?
            WHERE id = ?
        """, (
            data["name"].strip(),
            data["email"].strip().lower(),
            data["phone"].strip(),
            data["gender"].strip(),
            data["dob"].strip(),
            int(data["department_id"]),
            int(data["course_id"]),
            int(data["year"]),
            data["section"].strip().upper(),
            int(data["admission_year"]),
            data["address"].strip(),
            student_id
        ))
        conn.commit()
    finally:
        conn.close()

    generate_system_alerts()


def delete_student(student_id):
    """Delete a student and associated attendance, marks, and alerts."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM alerts WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
    finally:
        conn.close()

    generate_system_alerts()


# ==========================================
# Departments & Courses CRUD
# ==========================================

def get_all_departments():
    """Retrieve all departments with student count."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT d.*, COUNT(s.id) as student_count
        FROM departments d
        LEFT JOIN students s ON s.department_id = d.id
        GROUP BY d.id
        ORDER BY d.name ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_courses():
    """Retrieve all courses with department info and student count."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT c.*, d.name as department_name, d.code as department_code, COUNT(s.id) as student_count
        FROM courses c
        JOIN departments d ON c.department_id = d.id
        LEFT JOIN students s ON s.course_id = c.id
        GROUP BY c.id
        ORDER BY c.name ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_department(name, code, hod):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO departments (name, code, hod) VALUES (?, ?, ?)",
                     (name.strip(), code.strip().upper(), hod.strip()))
        conn.commit()
    finally:
        conn.close()


def update_department(dept_id, name, code, hod):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE departments SET name = ?, code = ?, hod = ? WHERE id = ?",
                     (name.strip(), code.strip().upper(), hod.strip(), dept_id))
        conn.commit()
    finally:
        conn.close()


def delete_department(dept_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
        conn.commit()
    finally:
        conn.close()


def add_course(name, code, department_id, duration):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO courses (name, code, department_id, duration) VALUES (?, ?, ?, ?)",
                     (name.strip(), code.strip().upper(), int(department_id), duration.strip()))
        conn.commit()
    finally:
        conn.close()


def update_course(course_id, name, code, department_id, duration):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE courses SET name = ?, code = ?, department_id = ?, duration = ? WHERE id = ?",
                     (name.strip(), code.strip().upper(), int(department_id), duration.strip(), course_id))
        conn.commit()
    finally:
        conn.close()


def delete_course(course_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
    finally:
        conn.close()


# ==========================================
# Attendance Operations
# ==========================================

def get_all_attendance():
    """Retrieve attendance for all students with status tags."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            a.*,
            s.name as student_name,
            s.register_number,
            d.code as department_code,
            d.name as department_name,
            s.year,
            s.section
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN departments d ON s.department_id = d.id
        ORDER BY s.name ASC
    """).fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        pct = item["percentage"]
        if pct >= 75:
            item["attendance_status"] = "Good"
            item["badge_class"] = "badge-success"
        elif pct >= 60:
            item["attendance_status"] = "Warning"
            item["badge_class"] = "badge-warning"
        else:
            item["attendance_status"] = "Low"
            item["badge_class"] = "badge-danger"
        result.append(item)
    return result


def update_student_attendance(student_id, total_classes, present):
    """Update attendance record, calculating absent classes and percentage."""
    total = max(0, int(total_classes))
    pres = max(0, min(int(present), total))
    absent = total - pres
    percentage = round((pres / total) * 100, 2) if total > 0 else 0.0

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO attendance (student_id, total_classes, present, absent, percentage)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                total_classes = excluded.total_classes,
                present = excluded.present,
                absent = excluded.absent,
                percentage = excluded.percentage
        """, (student_id, total, pres, absent, percentage))
        conn.commit()
    finally:
        conn.close()

    generate_system_alerts()


# ==========================================
# Marks & Performance Operations
# ==========================================

def get_all_marks():
    """Retrieve all subject marks with joined student information."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            m.*,
            s.name as student_name,
            s.register_number,
            d.code as department_code
        FROM marks m
        JOIN students s ON m.student_id = s.id
        JOIN departments d ON s.department_id = d.id
        ORDER BY s.name ASC, m.subject ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_marks(student_id):
    """Retrieve marks list for a specific student."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM marks WHERE student_id = ? ORDER BY subject ASC
    """, (student_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_or_update_mark(student_id, subject, internal_mark, external_mark):
    """
    Save or update mark record.
    Calculates total = internal + external, and dynamically calculates letter grade.
    """
    internal = max(0.0, float(internal_mark))
    external = max(0.0, float(external_mark))
    total = round(internal + external, 2)
    grade = calculate_grade(total)

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO marks (student_id, subject, internal_mark, external_mark, total, grade)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, subject) DO UPDATE SET
                internal_mark = excluded.internal_mark,
                external_mark = excluded.external_mark,
                total = excluded.total,
                grade = excluded.grade
        """, (int(student_id), subject.strip(), internal, external, total, grade))
        conn.commit()
    finally:
        conn.close()

    generate_system_alerts()


def delete_mark(mark_id):
    """Delete an individual mark record."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM marks WHERE id = ?", (mark_id,))
        conn.commit()
    finally:
        conn.close()

    generate_system_alerts()


# ==========================================
# Alerts & System Notifications
# ==========================================

def get_all_alerts(limit=50):
    """Retrieve active alerts with student details."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            a.*,
            s.name as student_name,
            s.register_number,
            d.code as department_code
        FROM alerts a
        LEFT JOIN students s ON a.student_id = s.id
        LEFT JOIN departments d ON s.department_id = d.id
        ORDER BY
            CASE a.severity
                WHEN 'Critical' THEN 1
                WHEN 'Warning' THEN 2
                ELSE 3
            END,
            a.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==========================================
# Dashboard & Analytics Statistics
# ==========================================

def get_dashboard_data():
    """
    Compute real-time statistics from SQLite:
    - total_students
    - total_courses
    - total_departments
    - average_attendance
    - excellent_students
    - students_needing_attention
    - at_risk_students
    - recent_students
    - recent_alerts
    - department_distribution
    - attendance_distribution
    """
    conn = get_db_connection()

    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_courses = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    total_departments = conn.execute("SELECT COUNT(*) FROM departments").fetchone()[0]

    avg_att_row = conn.execute("SELECT AVG(percentage) FROM attendance").fetchone()[0]
    average_attendance = round(float(avg_att_row), 1) if avg_att_row is not None else 0.0

    # Recent 5 students
    recent_students_rows = conn.execute("""
        SELECT s.id, s.name, s.register_number, s.year, s.section, s.created_at,
               d.code as department_code, c.name as course_name
        FROM students s
        LEFT JOIN departments d ON s.department_id = d.id
        LEFT JOIN courses c ON s.course_id = c.id
        ORDER BY s.id DESC
        LIMIT 5
    """).fetchall()
    recent_students = [dict(r) for r in recent_students_rows]

    # Department student distribution
    dept_rows = conn.execute("""
        SELECT d.code, d.name, COUNT(s.id) as count
        FROM departments d
        LEFT JOIN students s ON s.department_id = d.id
        GROUP BY d.id
        ORDER BY d.code ASC
    """).fetchall()
    dept_distribution = [{"label": r["code"], "name": r["name"], "count": r["count"]} for r in dept_rows]

    # Attendance distribution: Good (>=75%), Warning (60-74.9%), Low (<60%)
    att_good = conn.execute("SELECT COUNT(*) FROM attendance WHERE percentage >= 75").fetchone()[0]
    att_warning = conn.execute("SELECT COUNT(*) FROM attendance WHERE percentage >= 60 AND percentage < 75").fetchone()[0]
    att_low = conn.execute("SELECT COUNT(*) FROM attendance WHERE percentage < 60").fetchone()[0]

    attendance_distribution = {
        "good": att_good,
        "warning": att_warning,
        "low": att_low
    }

    conn.close()

    # Calculate status counts across all students
    all_students = get_all_students()
    excellent_count = sum(1 for s in all_students if s["status"] == "Excellent")
    needing_attention_count = sum(1 for s in all_students if s["status"] in ("Needs Attention", "At Risk"))
    at_risk_count = sum(1 for s in all_students if s["status"] == "At Risk")

    recent_alerts = get_all_alerts(limit=5)

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_departments": total_departments,
        "average_attendance": average_attendance,
        "excellent_students": excellent_count,
        "students_needing_attention": needing_attention_count,
        "at_risk_students": at_risk_count,
        "recent_students": recent_students,
        "recent_alerts": recent_alerts,
        "department_distribution": dept_distribution,
        "attendance_distribution": attendance_distribution
    }


def get_performance_analytics():
    """
    Retrieve aggregated marks & performance data for analytics dashboard:
    - Overall average marks
    - Highest mark
    - Lowest mark
    - Total subjects evaluated
    - Passed subjects count (grade != 'F')
    - Failed subjects count (grade == 'F')
    - Subject-wise average marks
    - Grade distribution
    """
    conn = get_db_connection()

    stats_row = conn.execute("""
        SELECT
            ROUND(AVG(total), 1) as avg_mark,
            MAX(total) as highest_mark,
            MIN(total) as lowest_mark,
            COUNT(*) as total_evaluations,
            SUM(CASE WHEN grade != 'F' THEN 1 ELSE 0 END) as passed_count,
            SUM(CASE WHEN grade = 'F' THEN 1 ELSE 0 END) as failed_count
        FROM marks
    """).fetchone()

    # Subject-wise marks
    subject_rows = conn.execute("""
        SELECT subject, ROUND(AVG(total), 1) as avg_score, MAX(total) as max_score, MIN(total) as min_score
        FROM marks
        GROUP BY subject
        ORDER BY subject ASC
    """).fetchall()

    # Grade distribution
    grade_order = ["A+", "A", "B+", "B", "C", "F"]
    grade_counts = {g: 0 for g in grade_order}
    g_rows = conn.execute("""
        SELECT grade, COUNT(*) as count
        FROM marks
        GROUP BY grade
    """).fetchall()
    for g in g_rows:
        if g["grade"] in grade_counts:
            grade_counts[g["grade"]] = g["count"]

    conn.close()

    dashboard_stats = get_dashboard_data()

    return {
        "average_mark": stats_row["avg_mark"] or 0.0,
        "highest_mark": stats_row["highest_mark"] or 0.0,
        "lowest_mark": stats_row["lowest_mark"] or 0.0,
        "total_evaluations": stats_row["total_evaluations"] or 0,
        "passed_count": stats_row["passed_count"] or 0,
        "failed_count": stats_row["failed_count"] or 0,
        "average_attendance": dashboard_stats["average_attendance"],
        "subject_analysis": [dict(r) for r in subject_rows],
        "grade_distribution": grade_counts,
        "department_distribution": dashboard_stats["department_distribution"],
        "attendance_distribution": dashboard_stats["attendance_distribution"]
    }
