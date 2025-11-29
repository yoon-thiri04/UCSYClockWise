# UCSYClockWise⏰
![Built with Django](https://img.shields.io/badge/Built%20With-Django-092E20?style=for-the-badge&logo=django&logoColor=white)

> **“Intelligent Timetable Generator for University of Computer Studies, Yangon (UCSY)”** 🏛

****  
<img width="1000" height="600" alt="ucsy" src="https://github.com/user-attachments/assets/43f85d73-e01c-44ac-bb08-c177334e8b4f" />

🎨 [Explore our UIUX Design for UCSYClockWise](https://www.figma.com/design/rdQfykXAF34phCCkZ5r0rx/Untitled?t=u5K9ILcT4ytLc5dK-0)


## Overview  
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
- Showing the most freetime of the classroom for weekdays
---

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Django
- **Database**: SQLite

---


