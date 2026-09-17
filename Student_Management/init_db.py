"""
Student Management System - Database Initializer and Seeder
Creates tables and seeds initial realistic demo data for departments, courses,
students, attendance, marks, and generates initial system alerts.
"""

import os
from database import (
    get_db_connection,
    init_database_schema,
    calculate_grade,
    generate_system_alerts,
    DB_PATH
)


def seed_database():
    """Seed sample departments, courses, students, attendance, and marks."""
    print(f"Connecting to database at {DB_PATH}...")
    init_database_schema()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if data already exists
    student_count = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if student_count > 0:
        print(f"Database already contains {student_count} students. Re-generating alerts...")
        conn.close()
        generate_system_alerts()
        print("Database is ready!")
        return

    print("Seeding sample departments...")
    departments = [
        ("Computer Science and Engineering", "CSE", "Dr. Rajesh Sharma"),
        ("Computer Science and Business Systems", "CSBS", "Dr. Priya Sundaram"),
        ("Information Technology", "IT", "Dr. Arvind Kumar"),
        ("Electronics and Communication Engineering", "ECE", "Dr. Meenakshi Raman"),
        ("Electrical and Electronics Engineering", "EEE", "Dr. K. Venkatesh"),
        ("Mechanical Engineering", "MECH", "Dr. S. Balaji"),
        ("Civil Engineering", "CIVIL", "Dr. R. Natarajan"),
    ]
    cursor.executemany(
        "INSERT INTO departments (name, code, hod) VALUES (?, ?, ?)",
        departments
    )

    # Get department IDs
    dept_map = {row["code"]: row["id"] for row in cursor.execute("SELECT id, code FROM departments").fetchall()}

    print("Seeding sample courses...")
    courses = [
        ("B.E. Computer Science and Engineering", "BE-CSE", dept_map["CSE"], "4 Years"),
        ("B.Tech Computer Science & Business Systems", "BTECH-CSBS", dept_map["CSBS"], "4 Years"),
        ("B.Tech Information Technology", "BTECH-IT", dept_map["IT"], "4 Years"),
        ("B.E. Electronics & Communication Engineering", "BE-ECE", dept_map["ECE"], "4 Years"),
        ("B.E. Electrical & Electronics Engineering", "BE-EEE", dept_map["EEE"], "4 Years"),
        ("B.E. Mechanical Engineering", "BE-MECH", dept_map["MECH"], "4 Years"),
        ("B.E. Civil Engineering", "BE-CIVIL", dept_map["CIVIL"], "4 Years"),
    ]
    cursor.executemany(
        "INSERT INTO courses (name, code, department_id, duration) VALUES (?, ?, ?, ?)",
        courses
    )

    course_map = {row["code"]: row["id"] for row in cursor.execute("SELECT id, code FROM courses").fetchall()}

    print("Seeding 12 realistic students with varying performance profiles...")
    # Students data:
    # (name, reg_no, email, phone, gender, dob, dept_code, course_code, year, section, adm_year, address, total_cls, pres_cls)
    students_data = [
        # 1. Excellent student (high marks, high attendance)
        ("Aarav Patel", "REG2023CSE001", "aarav.patel@example.com", "9876543210", "Male", "2004-03-15",
         "CSE", "BE-CSE", 3, "A", 2023, "12 Park Avenue, Chennai, Tamil Nadu", 90, 86),

        # 2. Excellent student
        ("Sneha Iyer", "REG2023CSE002", "sneha.iyer@example.com", "9876543211", "Female", "2004-07-22",
         "CSE", "BE-CSE", 3, "A", 2023, "45 Lake View Road, Coimbatore, Tamil Nadu", 90, 84),

        # 3. Good student (solid marks and attendance)
        ("Rahul Verma", "REG2023IT001", "rahul.verma@example.com", "9876543212", "Male", "2004-11-05",
         "IT", "BTECH-IT", 3, "B", 2023, "88 Gandhi Nagar, Madurai, Tamil Nadu", 90, 78),

        # 4. Good student
        ("Ananya Rao", "REG2024CSBS001", "ananya.rao@example.com", "9876543213", "Female", "2005-01-19",
         "CSBS", "BTECH-CSBS", 2, "A", 2024, "34 Green Meadows, Bengaluru, Karnataka", 85, 72),

        # 5. Warning attendance (60-74%)
        ("Karthik Subramanian", "REG2023ECE001", "karthik.s@example.com", "9876543214", "Male", "2004-05-30",
         "ECE", "BE-ECE", 3, "A", 2023, "17 West Hill, Salem, Tamil Nadu", 90, 62),

        # 6. Needs attention (lower marks, moderate attendance)
        ("Divya Nambiar", "REG2024CSE003", "divya.n@example.com", "9876543215", "Female", "2005-08-14",
         "CSE", "BE-CSE", 2, "B", 2024, "23 River Road, Trichy, Tamil Nadu", 85, 61),

        # 7. At risk (low attendance < 60% and failure)
        ("Vikramaditya Singh", "REG2022MECH001", "vikram.singh@example.com", "9876543216", "Male", "2003-12-10",
         "MECH", "BE-MECH", 4, "A", 2022, "9 South Circular Road, Chennai, Tamil Nadu", 95, 52),

        # 8. Excellent student
        ("Pooja Krishnan", "REG2023IT002", "pooja.k@example.com", "9876543217", "Female", "2004-09-02",
         "IT", "BTECH-IT", 3, "A", 2023, "56 Rose Garden, Tirunelveli, Tamil Nadu", 90, 88),

        # 9. Needs attention (low marks)
        ("Mohammed Farhan", "REG2024EEE001", "m.farhan@example.com", "9876543218", "Male", "2005-04-18",
         "EEE", "BE-EEE", 2, "A", 2024, "104 Anna Salai, Vellore, Tamil Nadu", 85, 68),

        # 10. Good student
        ("Keerthana Reddy", "REG2023CIVIL001", "keerthana.r@example.com", "9876543219", "Female", "2004-02-28",
         "CIVIL", "BE-CIVIL", 3, "A", 2023, "72 Temple Street, Erode, Tamil Nadu", 90, 77),

        # 11. Warning attendance
        ("Siddharth Menon", "REG2024CSBS002", "sid.menon@example.com", "9876543220", "Male", "2005-06-11",
         "CSBS", "BTECH-CSBS", 2, "B", 2024, "15 Beach Road, Kochi, Kerala", 85, 59),

        # 12. Good student
        ("Roshni Chawla", "REG2025CSE004", "roshni.c@example.com", "9876543221", "Female", "2006-01-25",
         "CSE", "BE-CSE", 1, "A", 2025, "81 High Town, Thanjavur, Tamil Nadu", 60, 56),
    ]

    student_id_map = {}
    for item in students_data:
        name, reg_no, email, phone, gender, dob, dept_code, crs_code, yr, sec, adm_yr, addr, tot_cls, pres_cls = item
        cursor.execute("""
            INSERT INTO students (
                name, register_number, email, phone, gender, dob,
                department_id, course_id, year, section, admission_year, address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, reg_no, email, phone, gender, dob, dept_map[dept_code], course_map[crs_code], yr, sec, adm_yr, addr))
        s_id = cursor.lastrowid
        student_id_map[reg_no] = s_id

        # Insert attendance
        abs_cls = tot_cls - pres_cls
        pct = round((pres_cls / tot_cls) * 100, 2)
        cursor.execute("""
            INSERT INTO attendance (student_id, total_classes, present, absent, percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (s_id, tot_cls, pres_cls, abs_cls, pct))

    print("Seeding subject marks for all students...")
    # Subjects
    subjects = ["Python", "Java", "DBMS", "Data Structures", "Computer Networks", "Mathematics"]

    # Pre-defined marks profile per student
    # (internal out of 40, external out of 60)
    student_marks_profiles = {
        "REG2023CSE001": [(38, 56), (36, 55), (39, 58), (37, 57), (38, 54), (35, 53)],  # ~92-97 A+
        "REG2023CSE002": [(35, 52), (37, 51), (36, 54), (38, 53), (34, 50), (36, 52)],  # ~84-91 A/A+
        "REG2023IT001":  [(32, 48), (30, 45), (34, 50), (33, 47), (29, 44), (31, 46)],  # ~73-84 B+/A
        "REG2024CSBS001":[(31, 46), (33, 49), (28, 42), (30, 45), (32, 47), (29, 43)],  # ~70-82 B+/A
        "REG2023ECE001": [(26, 40), (28, 42), (25, 38), (27, 41), (24, 39), (23, 37)],  # ~60-70 B/B+
        "REG2024CSE003": [(22, 34), (20, 32), (24, 35), (21, 31), (19, 33), (18, 30)],  # ~48-59 C/F (needs attention)
        "REG2022MECH001":[(15, 25), (14, 28), (18, 26), (12, 22), (16, 29), (13, 24)],  # ~34-45 F (At risk!)
        "REG2023IT002":  [(39, 57), (38, 56), (37, 55), (39, 58), (36, 54), (38, 55)],  # ~90-97 A+
        "REG2024EEE001": [(24, 32), (22, 30), (25, 33), (20, 28), (23, 31), (21, 29)],  # ~48-58 C/F
        "REG2023CIVIL001":[(30, 47), (29, 45), (31, 48), (28, 44), (32, 46), (30, 45)], # ~72-79 B+
        "REG2024CSBS002":[(23, 35), (24, 36), (22, 34), (25, 37), (21, 33), (20, 32)],  # ~52-62 C/B
        "REG2025CSE004": [(33, 50), (34, 49), (32, 48), (35, 52), (31, 47), (33, 49)],  # ~78-87 B+/A
    }

    for reg_no, marks_list in student_marks_profiles.items():
        s_id = student_id_map[reg_no]
        for idx, sub in enumerate(subjects):
            internal, external = marks_list[idx]
            tot = round(internal + external, 2)
            grd = calculate_grade(tot)
            cursor.execute("""
                INSERT INTO marks (student_id, subject, internal_mark, external_mark, total, grade)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (s_id, sub, internal, external, tot, grd))

    conn.commit()
    conn.close()

    print("Generating dynamic system alerts...")
    generate_system_alerts()

    print("Database initialization and realistic data seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
