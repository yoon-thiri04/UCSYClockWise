# UCSY ClockWise ⏰

![Built with Django](https://img.shields.io/badge/Built%20With-Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Status](https://img.shields.io/badge/Project-In_Development-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Intelligent Timetable Generator for University of Computer Studies, Yangon (UCSY)**  

## Introduction  
UCSYClockWise is an automated timetable generation system designed for UCSY to streamline the complex process of scheduling lectures, labs, and instructor assignments while adhering to university-specific constraints.

### Key Challenges Addressed:
- Dynamic classroom allocation per semester (General/Major-specific)
- Handling Supporting/Elective/Major/General courses with varying requirements
- Lab room scheduling & instructor availability (on-campus or not)
- Conflict-free timetable generation with swap/merge functionality

## Features

### User Roles & Functions
| **Role** | Responsibilities |
|------|------------------|
| **Staff** | Register courses, instructors (on/off-campus), classrooms (Lab/Lecture), and assign departments with courses |
| **Admin** | Match instructors/lab room with courses, generate timetables, swap/merge slots |
| **Instructor** | View personal and others' schedules, request temporary swaps with colleagues |
| **Student** | View/Download their timetables |

### Core Functionalities
- **Smart Timetable Generation**:
  - Auto-assigns instructors/labs based on credit hours, and availability
  - Constraints: Remote instructors avoid early slots, lab room conflicts, max 20 hours/instructor
- **Swap/Merge Tools**:
  - **Swap**: Admin can reassign slots if instructors/labs are free
  - **Merge**: Combine low-enrollment major classes into shared slots
- **Semester-Specific Logic**:
  - Major splits start from Semester 5 (e.g., SE, KE, CyberSecurity)
  - General subjects (Pre-Semester 5) vs. Major/Supporting/Elective courses

- **🎓 Special Case: Semester 10**
  - No timetable needed
  - Students upload their resume
  - Companies view & assign students
  - One instructor is auto-assigned per student group

---

### Additional Modules 
- Assignment/Event notifications (in-app messaging)


## Tech Stack
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Django
- **Database**: SQLite

---
## 🧑‍💻 Development Team

| **Role**        | **Members**                          |
|-----------------|---------------------------------------|
| UI/UX Design    | Soe Sett Lynn                        |
| Frontend        | Hla Myat Thwe, Phyo Thant Kyaw       |
| Backend         | Yoon Thiri Aung, Thet Su Lwin        |

---

## Database Design (Django Models)


