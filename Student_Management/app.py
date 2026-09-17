"""
Student Management System - Main Flask Application
College Mini-Project Prototype
A clean, modular web application for student record management,
attendance tracking, marks evaluation, and dynamic academic analytics.
"""

import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort
)
from database import (
    init_database_schema,
    validate_student_data,
    get_all_students,
    get_student_by_id,
    add_student,
    update_student,
    delete_student,
    get_all_departments,
    add_department,
    update_department,
    delete_department,
    get_all_courses,
    add_course,
    update_course,
    delete_course,
    get_all_attendance,
    update_student_attendance,
    get_all_marks,
    get_student_marks,
    save_or_update_mark,
    delete_mark,
    get_all_alerts,
    get_dashboard_data,
    get_performance_analytics,
    generate_system_alerts
)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "student-management-secret-key-2024")

# Automatically ensure database schema is created on application startup
with app.app_context():
    init_database_schema()
    generate_system_alerts()


# ==============================================================================
# WEB PAGE ROUTES (UI)
# ==============================================================================

@app.route("/")
def dashboard():
    """Main Dashboard view showing summary statistics, activity, and dynamic charts."""
    dashboard_data = get_dashboard_data()
    return render_template("index.html", active_page="dashboard", data=dashboard_data)


@app.route("/students")
def students_list():
    """Student Directory with search, multi-field filters, and status badges."""
    search = request.args.get("search", "").strip()
    dept = request.args.get("dept", "all")
    year = request.args.get("year", "all")
    section = request.args.get("section", "all")
    status = request.args.get("status", "all")

    students = get_all_students(
        search=search if search else None,
        dept_filter=dept if dept != "all" else None,
        year_filter=year if year != "all" else None,
        section_filter=section if section != "all" else None,
        status_filter=status if status != "all" else None
    )
    departments = get_all_departments()

    return render_template(
        "students.html",
        active_page="students",
        students=students,
        departments=departments,
        current_search=search,
        current_dept=dept,
        current_year=year,
        current_status=status
    )


@app.route("/students/add", methods=["GET", "POST"])
def add_student_view():
    """Add new student view and form processing."""
    departments = get_all_departments()
    courses = get_all_courses()

    if request.method == "POST":
        form_data = request.form.to_dict()
        is_valid, error_msg = validate_student_data(form_data, is_update=False)

        if not is_valid:
            flash(error_msg, "danger")
            return render_template(
                "add_student.html",
                active_page="add_student",
                departments=departments,
                courses=courses,
                form_data=form_data
            )

        try:
            new_id = add_student(form_data)
            flash(f"Student '{form_data['name']}' registered successfully with Reg No: {form_data['register_number'].upper()}!", "success")
            return redirect(url_for("student_profile_view", student_id=new_id))
        except Exception as e:
            flash(f"Error registering student: {str(e)}", "danger")
            return render_template(
                "add_student.html",
                active_page="add_student",
                departments=departments,
                courses=courses,
                form_data=form_data
            )

    return render_template(
        "add_student.html",
        active_page="add_student",
        departments=departments,
        courses=courses,
        form_data=None
    )


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student_view(student_id):
    """Edit existing student details."""
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students_list"))

    departments = get_all_departments()
    courses = get_all_courses()

    if request.method == "POST":
        form_data = request.form.to_dict()
        is_valid, error_msg = validate_student_data(form_data, is_update=True, current_id=student_id)

        if not is_valid:
            flash(error_msg, "danger")
            return render_template(
                "edit_student.html",
                active_page="students",
                student=student,
                departments=departments,
                courses=courses
            )

        try:
            update_student(student_id, form_data)
            flash(f"Student '{form_data['name']}' updated successfully!", "success")
            return redirect(url_for("student_profile_view", student_id=student_id))
        except Exception as e:
            flash(f"Error updating student: {str(e)}", "danger")

    return render_template(
        "edit_student.html",
        active_page="students",
        student=student,
        departments=departments,
        courses=courses
    )


@app.route("/students/delete/<int:student_id>", methods=["GET", "POST"])
def delete_student_action(student_id):
    """Delete student and redirect with notification."""
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "danger")
    else:
        name = student["name"]
        delete_student(student_id)
        flash(f"Student '{name}' has been successfully deleted.", "info")

    return redirect(url_for("students_list"))


@app.route("/students/<int:student_id>")
def student_profile_view(student_id):
    """Detailed Student Profile with personal data, attendance, and subject marks."""
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students_list"))

    marks = get_student_marks(student_id)
    return render_template(
        "student_profile.html",
        active_page="students",
        student=student,
        marks=marks
    )


@app.route("/courses")
def courses_view():
    """Course Management view."""
    courses = get_all_courses()
    departments = get_all_departments()
    return render_template("courses.html", active_page="courses", courses=courses, departments=departments)


@app.route("/courses/add", methods=["POST"])
def add_course_action():
    """Create a new course."""
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    dept_id = request.form.get("department_id")
    duration = request.form.get("duration", "").strip()

    if not all([name, code, dept_id, duration]):
        flash("All course fields are required.", "danger")
    else:
        try:
            add_course(name, code, dept_id, duration)
            flash(f"Course '{name}' ({code}) added successfully.", "success")
        except Exception as e:
            flash(f"Error adding course: {str(e)}", "danger")

    return redirect(url_for("courses_view"))


@app.route("/courses/edit/<int:course_id>", methods=["POST"])
def edit_course_action(course_id):
    """Update course details."""
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    dept_id = request.form.get("department_id")
    duration = request.form.get("duration", "").strip()

    try:
        update_course(course_id, name, code, dept_id, duration)
        flash(f"Course '{name}' updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating course: {str(e)}", "danger")

    return redirect(url_for("courses_view"))


@app.route("/courses/delete/<int:course_id>")
def delete_course_action(course_id):
    """Delete a course."""
    try:
        delete_course(course_id)
        flash("Course removed successfully.", "info")
    except Exception as e:
        flash(f"Cannot delete course: It may have active students enrolled ({str(e)}).", "danger")

    return redirect(url_for("courses_view"))


@app.route("/departments")
def departments_view():
    """Department Management view."""
    departments = get_all_departments()
    return render_template("departments.html", active_page="departments", departments=departments)


@app.route("/departments/add", methods=["POST"])
def add_department_action():
    """Create a new department."""
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    hod = request.form.get("hod", "").strip()

    if not all([name, code, hod]):
        flash("All department fields are required.", "danger")
    else:
        try:
            add_department(name, code, hod)
            flash(f"Department '{name}' ({code}) added successfully.", "success")
        except Exception as e:
            flash(f"Error adding department: {str(e)}", "danger")

    return redirect(url_for("departments_view"))


@app.route("/departments/edit/<int:dept_id>", methods=["POST"])
def edit_department_action(dept_id):
    """Update department details."""
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    hod = request.form.get("hod", "").strip()

    try:
        update_department(dept_id, name, code, hod)
        flash(f"Department '{name}' updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating department: {str(e)}", "danger")

    return redirect(url_for("departments_view"))


@app.route("/departments/delete/<int:dept_id>")
def delete_department_action(dept_id):
    """Delete a department."""
    try:
        delete_department(dept_id)
        flash("Department removed successfully.", "info")
    except Exception as e:
        flash(f"Cannot delete department: It may have active students/courses ({str(e)}).", "danger")

    return redirect(url_for("departments_view"))


@app.route("/attendance")
def attendance_view():
    """Attendance Management view."""
    attendance_list = get_all_attendance()
    return render_template("attendance.html", active_page="attendance", attendance_list=attendance_list)


@app.route("/attendance/update/<int:student_id>", methods=["POST"])
def update_attendance_action(student_id):
    """Update student attendance."""
    total = request.form.get("total_classes", 0)
    present = request.form.get("present", 0)

    try:
        update_student_attendance(student_id, total, present)
        flash("Attendance updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating attendance: {str(e)}", "danger")

    return redirect(request.referrer or url_for("attendance_view"))


@app.route("/marks")
def marks_view():
    """Marks & Evaluation Management view."""
    marks_list = get_all_marks()
    students = get_all_students()
    return render_template("marks.html", active_page="marks", marks_list=marks_list, students=students)


@app.route("/marks/save", methods=["POST"])
def save_mark_action():
    """Add or update student marks."""
    student_id = request.form.get("student_id")
    subject = request.form.get("subject", "").strip()
    internal = request.form.get("internal_mark", 0)
    external = request.form.get("external_mark", 0)
    redirect_url = request.form.get("redirect_url")

    try:
        save_or_update_mark(student_id, subject, internal, external)
        flash(f"Marks for subject '{subject}' saved successfully.", "success")
    except Exception as e:
        flash(f"Error saving marks: {str(e)}", "danger")

    return redirect(redirect_url or url_for("marks_view"))


@app.route("/marks/delete/<int:mark_id>")
def delete_mark_action(mark_id):
    """Delete an individual mark evaluation."""
    try:
        delete_mark(mark_id)
        flash("Mark record deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting mark: {str(e)}", "danger")

    return redirect(request.referrer or url_for("marks_view"))


@app.route("/performance")
def performance_view():
    """Student Performance Analysis and visual analytics."""
    analytics = get_performance_analytics()
    return render_template("performance.html", active_page="performance", data=analytics)


@app.route("/reports")
def reports_view():
    """Printable Academic Summary Reports."""
    dashboard_data = get_dashboard_data()
    perf_data = get_performance_analytics()
    students = get_all_students()
    departments = get_all_departments()

    return render_template(
        "reports.html",
        active_page="reports",
        data=dashboard_data,
        perf=perf_data,
        students=students,
        departments=departments
    )


@app.route("/about")
def about_view():
    """About Project Page with limitations disclaimer and roadmap."""
    return render_template("about.html", active_page="about")


# ==============================================================================
# REST API ENDPOINTS (JSON)
# ==============================================================================

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    """
    Returns real-time dashboard metrics:
    total_students, total_courses, total_departments, average_attendance,
    excellent_students, students_needing_attention, recent_students.
    """
    data = get_dashboard_data()
    return jsonify({
        "success": True,
        "total_students": data["total_students"],
        "total_courses": data["total_courses"],
        "total_departments": data["total_departments"],
        "average_attendance": data["average_attendance"],
        "excellent_students": data["excellent_students"],
        "students_needing_attention": data["students_needing_attention"],
        "recent_students": data["recent_students"]
    })


@app.route("/api/students", methods=["GET"])
def api_get_students():
    """Retrieve students list in JSON with optional search/filter params."""
    search = request.args.get("search")
    dept = request.args.get("dept")
    year = request.args.get("year")
    status = request.args.get("status")

    students = get_all_students(
        search=search,
        dept_filter=dept,
        year_filter=year,
        status_filter=status
    )
    return jsonify({"success": True, "count": len(students), "students": students})


@app.route("/api/students/<int:student_id>", methods=["GET"])
def api_get_student(student_id):
    """Retrieve detailed record for a single student."""
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"success": False, "error": "Student not found"}), 404

    marks = get_student_marks(student_id)
    return jsonify({
        "success": True,
        "student": student,
        "marks": marks
    })


@app.route("/api/students", methods=["POST"])
def api_create_student():
    """Create a new student via JSON payload."""
    data = request.get_json() or {}
    is_valid, error_msg = validate_student_data(data, is_update=False)

    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    try:
        new_id = add_student(data)
        created_student = get_student_by_id(new_id)
        return jsonify({
            "success": True,
            "message": "Student created successfully",
            "student": created_student
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def api_update_student(student_id):
    """Update student details via JSON payload."""
    existing = get_student_by_id(student_id)
    if not existing:
        return jsonify({"success": False, "error": "Student not found"}), 404

    data = request.get_json() or {}
    is_valid, error_msg = validate_student_data(data, is_update=True, current_id=student_id)

    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    try:
        update_student(student_id, data)
        updated = get_student_by_id(student_id)
        return jsonify({
            "success": True,
            "message": "Student updated successfully",
            "student": updated
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def api_delete_student(student_id):
    """Delete a student via API."""
    existing = get_student_by_id(student_id)
    if not existing:
        return jsonify({"success": False, "error": "Student not found"}), 404

    try:
        delete_student(student_id)
        return jsonify({"success": True, "message": f"Student ID {student_id} deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/courses", methods=["GET"])
def api_courses():
    """Retrieve all courses."""
    courses = get_all_courses()
    return jsonify({"success": True, "count": len(courses), "courses": courses})


@app.route("/api/departments", methods=["GET"])
def api_departments():
    """Retrieve all departments."""
    departments = get_all_departments()
    return jsonify({"success": True, "count": len(departments), "departments": departments})


@app.route("/api/attendance", methods=["GET"])
def api_attendance():
    """Retrieve all attendance records."""
    attendance = get_all_attendance()
    return jsonify({"success": True, "count": len(attendance), "attendance": attendance})


@app.route("/api/marks", methods=["GET"])
def api_marks():
    """Retrieve all marks records."""
    marks = get_all_marks()
    return jsonify({"success": True, "count": len(marks), "marks": marks})


@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    """Retrieve recent active alerts."""
    alerts = get_all_alerts(limit=50)
    return jsonify({"success": True, "count": len(alerts), "alerts": alerts})


# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Resource not found"}), 404
    return render_template("base.html", active_page=""), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    flash("An internal server error occurred. Please try again.", "danger")
    return redirect(url_for("dashboard"))


# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
