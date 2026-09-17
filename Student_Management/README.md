# Student Management System (SMS)

> **College Mini-Project Prototype**

An educational web-based academic administration platform built using **Python Flask**, **SQLite**, **HTML5**, **Vanilla CSS3**, and **Vanilla JavaScript**, with **Chart.js** via CDN.

---

## 1. Project Overview

The **Student Management System** is a responsive, web-based platform designed for colleges, universities, and academic departments.

It enables administrative and faculty staff to digitally manage:

* Student registrations
* Course information
* Department information
* Student attendance
* Semester examination marks
* Academic performance
* Student status and alerts
* Academic reports

The application computes key metrics dynamically:

* No hardcoded dashboard statistics.
* Automated letter grade classification from `A+` to `F`.
* Dynamic attendance percentage calculations.
* Attendance shortage identification.
* Student academic status indicators such as `Excellent`, `Good`, `Needs Attention`, and `At Risk`.

---

## 2. Problem Statement

Traditional academic record maintenance often relies on spreadsheets or manual paper records. This can lead to:

* Data redundancy and human errors.
* Difficulty tracking student attendance.
* Delayed identification of attendance shortages.
* Cumbersome marks and grade calculations.
* Difficulty generating consolidated academic reports.
* Limited visibility into overall student performance.

The **Student Management System** addresses these problems by providing a centralized and lightweight SQLite-based academic management platform.

---

## 3. Objectives

The main objectives of the project are:

* Implement complete **CRUD operations** for student records.
* Manage departments and courses.
* Track student attendance.
* Manage examination marks.
* Automatically calculate total marks and grades.
* Provide academic performance analytics.
* Identify students requiring academic attention.
* Provide interactive dashboard visualizations.
* Generate presentation-ready reports.
* Provide RESTful JSON API endpoints.
* Maintain student information in a centralized SQLite database.

---

## 4. Key Features

### 4.1 Modern Institutional Dashboard

The dashboard provides:

* Total Students
* Active Courses
* Departments
* Average Attendance
* Top Performers
* Students Requiring Attention
* Department-wise student distribution
* Attendance statistics
* Recent student registrations
* Automated academic alerts

### 4.2 Student Directory & Profile

The student management module provides:

* Add new students
* View student records
* Edit student information
* Delete student records
* Search students
* Filter students
* View detailed student profiles
* Display academic information
* Display attendance information
* Display marks and grades

Search and filtering can be performed using:

* Student Name
* Register Number
* Department
* Course
* Academic Year
* Section
* Status

### 4.3 Course & Department Management

The system supports:

* Course management
* Department management
* Department HOD information
* Course codes
* Course duration
* Student enrollment counts
* Relational connections between students, courses, and departments

### 4.4 Attendance Management

The attendance module provides:

* Total classes conducted
* Classes attended
* Classes absent
* Attendance percentage
* Attendance status
* Shortage identification

Attendance status:

* **Good:** `>= 75%`
* **Warning:** `60% - 74%`
* **Low:** `< 60%`

### 4.5 Marks Evaluation & Grading

The marks module supports:

* Internal assessment marks
* External examination marks
* Automatic total calculation
* Automatic letter grade calculation
* Subject-wise marks records

The standard calculation is:

**Total Mark = Internal Mark + External Mark**

where:

* Internal Maximum = 40
* External Maximum = 60
* Total Maximum = 100

### 4.6 Academic Performance Analytics

The performance module provides visual analytics using **Chart.js**.

The system can display:

* Subject-wise marks
* Average marks
* Highest marks
* Grade distribution
* Department-wise student count
* Attendance compliance

### 4.7 Reports

The system includes presentation-friendly reports with:

* Student academic information
* Attendance summaries
* Marks summaries
* Academic status
* Print-optimized layouts
* Institutional report formatting

### 4.8 RESTful JSON API

The application provides API endpoints for programmatic access to:

* Dashboard data
* Students
* Courses
* Departments
* Attendance
* Marks
* Alerts

---

## 5. Technologies Used

| Layer                 | Technology         | Details                                  |
| --------------------- | ------------------ | ---------------------------------------- |
| Backend Framework     | Python Flask       | Lightweight Python web framework         |
| Database              | SQLite 3           | Embedded relational database             |
| Frontend Markup       | HTML5              | Semantic and responsive HTML             |
| Frontend Styling      | Vanilla CSS3       | Custom responsive UI design              |
| Client-side Scripting | Vanilla JavaScript | Dynamic UI interactions and calculations |
| Data Visualization    | Chart.js 4.x       | Charts and academic analytics            |
| Template Engine       | Jinja2             | Flask-based HTML templating              |

### Technology Compliance

This project is intentionally developed without:

* React
* Angular
* Vue
* Node.js
* Bootstrap
* Tailwind CSS
* PHP
* Java

The project focuses on a lightweight **Flask + SQLite + HTML/CSS/JavaScript** architecture.

---

## 6. System Architecture

```text
                 [ Web Browser ]
                       |
                       | HTTP
                       |
                       v
              [ Flask Application ]
                    app.py
                       |
          +------------+------------+
          |                         |
          v                         v
   [ HTML Templates ]        [ REST API ]
       Jinja2                 /api/*
          |                         |
          +------------+------------+
                       |
                       v
             [ Business Logic ]
                database.py
                       |
                       v
              [ SQLite Database ]
                       |
                       v
        database/student_management.db
                       |
        +--------------+--------------+
        |              |              |
   departments      courses       students
                                      |
                            +---------+---------+
                            |                   |
                       attendance             marks
                                                |
                                             alerts
```

---

## 7. Database Design & Schema

The application uses an SQLite relational database with foreign key relationships.

### 7.1 Departments Table

```text
departments
```

Fields:

* `id` - INTEGER PRIMARY KEY AUTOINCREMENT
* `name` - TEXT NOT NULL UNIQUE
* `code` - TEXT NOT NULL UNIQUE
* `hod` - TEXT NOT NULL

### 7.2 Courses Table

```text
courses
```

Fields:

* `id` - INTEGER PRIMARY KEY AUTOINCREMENT
* `name` - TEXT NOT NULL
* `code` - TEXT NOT NULL UNIQUE
* `department_id` - INTEGER REFERENCES departments(id)
* `duration` - TEXT NOT NULL

### 7.3 Students Table

```text
students
```

Fields:

* `id` - INTEGER PRIMARY KEY AUTOINCREMENT
* `name` - TEXT NOT NULL
* `register_number` - TEXT NOT NULL UNIQUE
* `email` - TEXT NOT NULL
* `phone` - TEXT NOT NULL
* `gender` - TEXT NOT NULL
* `dob` - TEXT NOT NULL
* `department_id` - INTEGER REFERENCES departments(id)
* `course_id` - INTEGER REFERENCES courses(id)
* `year` - INTEGER NOT NULL
* `section` - TEXT NOT NULL
* `admission_year` - INTEGER NOT NULL
* `address` - TEXT NOT NULL
* `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### 7.4 Attendance Table

```text
attendance
```

Fields:

* `id` - INTEGER PRIMARY KEY AUTOINCREMENT
* `student_id` - INTEGER NOT NULL UNIQUE REFERENCE_
