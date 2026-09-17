"""
Comprehensive Integration Test Suite for Student Management System
Tests all web routes, form submissions, validations, CRUD operations,
marks calculations, attendance calculations, and REST API endpoints.
"""

import sys
import unittest
from app import app
from database import get_db_connection


class StudentManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_01_dashboard(self):
        """Verify Dashboard loads with 200 and required elements."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode()
        self.assertIn("Student Management System", html)
        self.assertIn("Institutional Dashboard", html)
        self.assertIn("deptChart", html)
        self.assertIn("attSummaryChart", html)
        print("[PASS] Dashboard view verified")

    def test_02_students_list_and_filters(self):
        """Verify Students list and filter parameters."""
        res = self.client.get("/students")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode()
        self.assertIn("Student Information Directory", html)
        self.assertIn("REG2023CSE001", html)

        # Test search filter parameter
        res_search = self.client.get("/students?search=Aarav")
        self.assertIn("Aarav Patel", res_search.data.decode())

        # Test department filter
        res_dept = self.client.get("/students?dept=1")
        self.assertEqual(res_dept.status_code, 200)
        print("[PASS] Student directory & filters verified")

    def test_03_student_add_validation_and_success(self):
        """Test Add Student form with validation failures and success."""
        # 1. Invalid email
        res_bad_email = self.client.post("/students/add", data={
            "name": "Invalid User",
            "register_number": "REGTEST001",
            "email": "invalid-email-no-at",
            "phone": "9876543210",
            "gender": "Male",
            "dob": "2004-01-01",
            "department_id": "1",
            "course_id": "1",
            "year": "2",
            "section": "A",
            "admission_year": "2024",
            "address": "Test Street",
            "total_classes": "60",
            "present": "55"
        }, follow_redirects=True)
        self.assertIn("Please enter a valid email address", res_bad_email.data.decode())

        # 2. Invalid phone
        res_bad_phone = self.client.post("/students/add", data={
            "name": "Invalid User",
            "register_number": "REGTEST001",
            "email": "valid@example.com",
            "phone": "123",
            "gender": "Male",
            "dob": "2004-01-01",
            "department_id": "1",
            "course_id": "1",
            "year": "2",
            "section": "A",
            "admission_year": "2024",
            "address": "Test Street",
            "total_classes": "60",
            "present": "55"
        }, follow_redirects=True)
        self.assertIn("Phone number must contain at least 10 valid digits", res_bad_phone.data.decode())

        # 3. Duplicate register number
        res_dup = self.client.post("/students/add", data={
            "name": "Duplicate User",
            "register_number": "REG2023CSE001",  # Existing
            "email": "dup@example.com",
            "phone": "9876543210",
            "gender": "Male",
            "dob": "2004-01-01",
            "department_id": "1",
            "course_id": "1",
            "year": "2",
            "section": "A",
            "admission_year": "2024",
            "address": "Test Street",
            "total_classes": "60",
            "present": "55"
        }, follow_redirects=True)
        self.assertIn("already assigned to another student", res_dup.data.decode())

        # 4. Valid student creation
        res_valid = self.client.post("/students/add", data={
            "name": "Rohan Deshmukh",
            "register_number": "REG2024CSE099",
            "email": "rohan.d@example.com",
            "phone": "9876543299",
            "gender": "Male",
            "dob": "2005-02-14",
            "department_id": "1",
            "course_id": "1",
            "year": "2",
            "section": "B",
            "admission_year": "2024",
            "address": "42 Marine Drive, Mumbai",
            "total_classes": "60",
            "present": "54"
        }, follow_redirects=True)
        self.assertEqual(res_valid.status_code, 200)
        self.assertIn("registered successfully", res_valid.data.decode())
        self.assertIn("Rohan Deshmukh", res_valid.data.decode())
        print("[PASS] Student validations and registration verified")

    def test_04_student_profile_edit_and_attendance(self):
        """Test student profile view, editing, and attendance update."""
        conn = get_db_connection()
        student = conn.execute("SELECT id FROM students WHERE register_number = 'REG2024CSE099'").fetchone()
        conn.close()
        self.assertIsNotNone(student)
        s_id = student["id"]

        # View profile
        res_prof = self.client.get(f"/students/{s_id}")
        self.assertEqual(res_prof.status_code, 200)
        self.assertIn("Rohan Deshmukh", res_prof.data.decode())

        # Edit student
        res_edit = self.client.post(f"/students/edit/{s_id}", data={
            "name": "Rohan A. Deshmukh",
            "register_number": "REG2024CSE099",
            "email": "rohan.new@example.com",
            "phone": "9876543299",
            "gender": "Male",
            "dob": "2005-02-14",
            "department_id": "1",
            "course_id": "1",
            "year": "2",
            "section": "A",
            "admission_year": "2024",
            "address": "42 Marine Drive, Mumbai"
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn("Rohan A. Deshmukh", res_edit.data.decode())

        # Update attendance
        res_att = self.client.post(f"/attendance/update/{s_id}", data={
            "total_classes": "80",
            "present": "72"
        }, follow_redirects=True)
        self.assertEqual(res_att.status_code, 200)

        # Check calculated percentage (72/80 = 90.0%)
        res_check = self.client.get(f"/students/{s_id}")
        self.assertIn("90.0%", res_check.data.decode())
        print("[PASS] Student profile, edit, and attendance update verified")

    def test_05_marks_calculation_and_grade(self):
        """Test recording marks and verifying automated grade calculation."""
        conn = get_db_connection()
        student = conn.execute("SELECT id FROM students WHERE register_number = 'REG2024CSE099'").fetchone()
        conn.close()
        s_id = student["id"]

        # Add mark: Internal 36, External 56 -> Total 92 -> Grade A+
        res_mark = self.client.post("/marks/save", data={
            "student_id": s_id,
            "subject": "Python",
            "internal_mark": "36",
            "external_mark": "56"
        }, follow_redirects=True)
        self.assertEqual(res_mark.status_code, 200)

        # Verify on marks page
        res_marks_page = self.client.get("/marks")
        html = res_marks_page.data.decode()
        self.assertIn("92.0", html)
        self.assertIn("A+", html)
        print("[PASS] Dynamic marks and letter grade calculation verified")

    def test_06_courses_and_departments(self):
        """Test Course and Department CRUD."""
        # Add course
        res_crs = self.client.post("/courses/add", data={
            "name": "M.E. Software Engineering",
            "code": "ME-SE",
            "department_id": "1",
            "duration": "2 Years"
        }, follow_redirects=True)
        self.assertEqual(res_crs.status_code, 200)
        self.assertIn("ME-SE", res_crs.data.decode())

        # Add department
        res_dept = self.client.post("/departments/add", data={
            "name": "Artificial Intelligence and Data Science",
            "code": "AIDS",
            "hod": "Dr. K. Swaminathan"
        }, follow_redirects=True)
        self.assertEqual(res_dept.status_code, 200)
        self.assertIn("AIDS", res_dept.data.decode())
        print("[PASS] Course and department management verified")

    def test_07_performance_reports_about(self):
        """Test Performance Analytics, Reports, and About views."""
        res_perf = self.client.get("/performance")
        self.assertEqual(res_perf.status_code, 200)
        self.assertIn("subjectMarksChart", res_perf.data.decode())
        self.assertIn("gradeDistributionChart", res_perf.data.decode())

        res_rep = self.client.get("/reports")
        self.assertEqual(res_rep.status_code, 200)
        self.assertIn("Academic Reports", res_rep.data.decode())
        self.assertIn("print-header", res_rep.data.decode())

        res_abt = self.client.get("/about")
        self.assertEqual(res_abt.status_code, 200)
        self.assertIn("Project Limitation Notice", res_abt.data.decode())
        print("[PASS] Performance, Reports, and About pages verified")

    def test_08_rest_api_endpoints(self):
        """Verify all JSON REST API endpoints."""
        # 1. Dashboard API
        d_res = self.client.get("/api/dashboard")
        self.assertEqual(d_res.status_code, 200)
        d_json = d_res.get_json()
        self.assertTrue(d_json["success"])
        self.assertGreaterEqual(d_json["total_students"], 12)

        # 2. Students API POST (Create)
        new_payload = {
            "name": "API Test Student",
            "register_number": "REGAPITEST01",
            "email": "api.test@example.com",
            "phone": "9876543200",
            "gender": "Female",
            "dob": "2005-05-15",
            "department_id": 1,
            "course_id": 1,
            "year": 1,
            "section": "A",
            "admission_year": 2024,
            "address": "API City, State",
            "total_classes": 50,
            "present": 45
        }
        create_res = self.client.post("/api/students", json=new_payload)
        self.assertEqual(create_res.status_code, 201)
        created_json = create_res.get_json()
        self.assertTrue(created_json["success"])
        test_id = created_json["student"]["id"]

        # 3. Students API PUT (Update)
        new_payload["name"] = "API Test Student Updated"
        put_res = self.client.put(f"/api/students/{test_id}", json=new_payload)
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.get_json()["student"]["name"], "API Test Student Updated")

        # 4. Students API DELETE
        del_res = self.client.delete(f"/api/students/{test_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.get_json()["success"])

        # 5. Other GET APIs
        for endpoint in ["/api/courses", "/api/departments", "/api/attendance", "/api/marks", "/api/alerts"]:
            r = self.client.get(endpoint)
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.get_json()["success"])

        print("[PASS] All REST API endpoints (GET, POST, PUT, DELETE) verified")

    def test_09_cleanup_test_student(self):
        """Cleanup temporary student created during test."""
        conn = get_db_connection()
        student = conn.execute("SELECT id FROM students WHERE register_number = 'REG2024CSE099'").fetchone()
        if student:
            self.client.get(f"/students/delete/{student['id']}")
        conn.close()
        print("[PASS] Test cleanup completed")


if __name__ == "__main__":
    unittest.main()
