# UCSYClockWise 🕰️


![Built with Django](https://img.shields.io/badge/Built%20With-Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Status](https://img.shields.io/badge/Project-In_Development-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

----

**Timetable Generator for the University of Computer Studies, Yangon (UCSY)**

---

## 📌 Overview

At UCSY, generating academic timetables every semester is a complex, manual task—balancing courses, classrooms, departments, lab availability, and instructor preferences. **UCSYClockWise** is a full-stack timetable generator designed to automate and simplify this process with accuracy, flexibility, and smart conflict resolution.

---

## 🎯 Project Goals

- Automatically generate conflict-free, well-structured timetables for all semesters and majors.
- Respect course types: **General**, **Major**, **Supporting**, and **Elective**.
- Handle classroom and lab allocations.
- Support course merging and slot swapping with validation.
- Provide role-based access for **Staff**, **Admin**, **Instructor**, and **Student**.

---

## 🧠 UCSY Course & Scheduling Logic

### 🏫 Semester & Course Types
- **General Courses**: Taught before majors are split (Sem 1–4).
- **Major Courses**: Required based on selected majors from Sem 5 onward.
- **Supporting & Elective Courses**: Optional, with Supporting allowing only 1 selection; no exams required.
- Courses change type depending on the semester.  
  _E.g.,_ `Web Development with Python` is **Major** in Sem 5, **Supporting** in Sem 7.

### 🧑‍🏫 Majors at UCSY
- Software Engineering (SE)
- Knowledge Engineering (KE)
- Cyber Security (CS), etc.

Students split into majors from **Semester 5** onward. Before that, rooms are allocated based on entrance scores (YKPT).

---

## 👥 User Roles & Functionalities

### 1. Staff

- Register:
  - Course details (including type and credit hours)
  - Instructor info (campus-based or not)
  - Department responsible for each course
  - Classroom & lab classification
- Rules:
  - Teachers from specific departments are fixed to specific courses (e.g., FCS handles CS, ITSM).

---

### 2. Admin

- Assign:
  - Semesters & classroom setups (e.g., KE+HPC or General)
  - Instructors and labs to courses (only valid based on credit hours and schedule)
- View & Generate:
  - Filters instructor/lab availability
  - Generates timetable using conflict-aware algorithms
- Features:
  - ⏳ **Swap**: Change class slots based on instructor/lab availability
  - 🔗 **Merge**: Combine lecture slots across classrooms when student count is low
- Other:
  - Manual override for last-minute merges
  - Export generated timetables

---

### 3. Instructor

- View personal and others' timetables
- Arrange informal temporary swaps (not affecting the database)
- Plan substitute teaching if needed

---

### 4. Student

- View/download their timetable
- Notifications from admin/teachers about assignments, tutorials, or events

---

### 🎓 Special Case: Semester 10

- No timetable needed
- Students upload their resume
- Companies view & assign students
- One instructor is auto-assigned per student group

---

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Django (local environment)
- **Database**: SQLite (Django default or customizable)
- **Timetable Logic**: Custom logic with Django ORM and scheduling algorithms

---

## 👥 Contributors

- **UI/UX Designer**: Soe Sett Lynn  
- **Frontend Developers**: Hla Myat Thwe, Phyo Thant Kyaw  
- **Backend Developers**: Yoon Thiri Aung (Me), Thet Su Lwin

---


