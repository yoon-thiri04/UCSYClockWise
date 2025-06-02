# UCSYClockWise 🕰️


![Built with Django](https://img.shields.io/badge/Built%20With-Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Status](https://img.shields.io/badge/Project-In_Development-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

----

**UCSYClockWise** is an intelligent Timetable Generator for the University of Computer Studies, Yangon (UCSY). It automates the complex task of creating academic timetables, ensuring efficiency, flexibility, and adherence to real-world academic constraints.

---

## 📘 Project Description

At UCSY, when the academic year begins, instructors manually draw up the timetable for the entire campus — a process that is time-consuming and prone to conflicts. UCSYClockWise solves this problem by generating automated, conflict-free timetables for classrooms, lab rooms, instructors, and students.

### Core Constraints Considered:

- Courses differ based on majors: SE, KE, HPC, etc.
- Course types include: **General**, **Major**, **Supporting**, **Elective**
- Subject sharing between majors (for common or shared lectures)
- Room types: Classrooms vs Lab Rooms
- Instructor availability and location (e.g., off-campus instructors should not be assigned early morning classes)
- Credit hour requirements for each course
- Semesters with and without major splits (e.g., pre-split general courses)
- Supporting/Elective subject choice per student (one supporting, multiple electives)

---

## 🚀 Main Features

### 👩‍🏫 User Roles & Functions

#### 1. **Staff**
- Register courses, instructors, and room information
- Specify the department responsible for each course
- Tag rooms as teaching rooms or lab rooms
- Define course types (major, general, supporting, elective) by semester

#### 2. **Admin**
- Set up semesters, classrooms, and assign majors (e.g., SE, KE+HPC, or General)
- Match instructors and lab rooms to specific courses, ensuring:
  - Instructor's weekly teaching hours do not exceed limits
  - Instructor belongs to the correct department
  - Lab rooms are not over-allocated
- **Generate**: Automatically create timetables with conflict resolution
- **Swap**: Adjust a specific time slot to another valid one (based on instructor availability, lab constraints, etc.)
- **Merge**: Combine lecture times across classrooms with fewer students
- Notify students and teachers (e.g., assignments, events)

#### 3. **Instructor**
- View personal and other instructors’ timetables
- Discuss temporary schedule swaps (manual, not admin-level Swap)
  
#### 4. **Student**
- Download their semester-specific timetable
- Semester 10 students upload resumes; companies can view and assign mentors

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


