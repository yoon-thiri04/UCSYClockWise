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
- Showing the most freetime of the classroom for weekdays
---

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Django
- **Database**: SQLite

---

## Check out our UIUX Design 
```
https://www.figma.com/design/rdQfykXAF34phCCkZ5r0rx/Untitled?t=u5K9ILcT4ytLc5dK-0
```

## Database Design (Django Models)

| Model Name                     | Field Name     | Field Type                             | Options/Relations                                                                   |
| ------------------------------ | -------------- | -------------------------------------- | ----------------------------------------------------------------------------------- |
| **Major**                      | name           | `CharField(max_length=100)`            |                                                                                     |
|                                |                | `__str__`                              | `self.name`                                                                         |
| **Semester**                   | name           | `CharField(max_length=10)`             | `unique=True`                                                                       |
|                                |                | `__str__`                              | `self.name`                                                                         |
| **Department**                 | name           | `CharField(max_length=100)`            |                                                                                     |
|                                |                | `__str__`                              | `self.name`                                                                         |
| **Course**                     | course\_id     | `CharField(max_length=10)`             | `unique=True`                                                                       |
|                                | name           | `CharField(max_length=150)`            |                                                                                     |
|                                | semester       | `ManyToManyField(Semester)`            | `blank=True`                                                                        |
|                                | major          | `ManyToManyField(Major)`               | `blank=True`                                                                        |
|                                | lab\_required  | `BooleanField(default=False)`          |                                                                                     |
|                                | credit\_hours  | `IntegerField(null=True, blank=True)`  |                                                                                     |
|                                | lab\_hours     | `IntegerField(null=True, blank=True)`  |                                                                                     |
|                                | lecture\_hours | `IntegerField(null=True, blank=True)`  |                                                                                     |
|                                | instructors    | `ManyToManyField(User)`                | `blank=True`                                                                        |
|                                |                | `__str__`                              | `f"{course_id} ({name})"`                                                           |
| **Classroom**                  | room\_number   | `CharField(max_length=15)`             | `unique=True`                                                                       |
|                                | majors         | `ManyToManyField(Major)`               | `blank=True`                                                                        |
|                                | semesters      | `ForeignKey(Semester)`                 | `null=True`, `blank=True`, `on_delete=CASCADE`                                      |
|                                | instructors    | `ManyToManyField(User)`                | `blank=True`                                                                        |
|                                | is\_lab        | `BooleanField(default=False)`          |                                                                                     |
|                                |                | `__str__`                              | `room_number + major names`                                                         |
| **CourseSemesterInfo**         | course         | `ForeignKey(Course)`                   | `on_delete=CASCADE`                                                                 |
|                                | semester       | `ForeignKey(Semester)`                 | `on_delete=CASCADE`                                                                 |
|                                | type           | `CharField(max_length=15)`             | `choices=course_type`, `default='general'`                                          |
|                                |                | `Meta`                                 | `unique_together = ('course', 'semester')`                                          |
|                                |                | `__str__`                              | `"course in semester as type"`                                                      |
| **LabroomUsed**                | lab\_room      | `CharField(max_length=15)`             |                                                                                     |
|                                | semester       | `ForeignKey(Semester)`                 | `null=True`, `blank=True`, `on_delete=CASCADE`                                      |
|                                | room           | `ForeignKey(Classroom)`                | `null=True`, `blank=True`, `on_delete=CASCADE`                                      |
|                                | course         | `ForeignKey(Course)`                   | `null=True`, `blank=True`, `on_delete=CASCADE`                                      |
|                                | lab\_hours     | `IntegerField(null=True, blank=True)`  |                                                                                     |
|                                | start\_time    | `DateTimeField(null=True, blank=True)` |                                                                                     |
|                                |                | `clean()`                              | Ensures unique lab assignment per course, room, and semester                        |
|                                |                | `__str__`                              | `lab_room`                                                                          |
| **UserProfile**                | user           | `OneToOneField(User)`                  | `on_delete=CASCADE`                                                                 |
|                                | department     | `ForeignKey(Department)`               | `null=True`, `blank=True`, `on_delete=SET_NULL`                                     |
|                                | classroom      | `ForeignKey(Classroom)`                | `null=True`, `blank=True`, `on_delete=SET_NULL`                                     |
|                                | semester       | `ForeignKey(Semester)`                 | `null=True`, `blank=True`, `on_delete=SET_NULL`                                     |
|                                | major          | `ForeignKey(Major)`                    | `null=True`, `blank=True`, `on_delete=SET_NULL`                                     |
|                                | within\_Campus | `BooleanField(default=False)`          |                                                                                     |
|                                |                | `__str__`                              | `user - department`                                                                 |
| **Timetable\_Schedule**        | semester       | `ForeignKey(Semester)`                 | `on_delete=CASCADE`                                                                 |
|                                | course         | `ForeignKey(Course)`                   | `null=True`, `blank=True`, `on_delete=CASCADE`                                      |
|                                | instructor     | `ForeignKey(User)`                     | `null=True`, `blank=True`, `on_delete=CASCADE`                                      |
|                                | classroom      | `ForeignKey(Classroom)`                | `related_name='main_class'`, `on_delete=CASCADE`                                    |
|                                | lab\_room      | `ForeignKey(Classroom)`                | `related_name='lab_matches'`, `null=True`, `blank=True`, `on_delete=CASCADE`        |
|                                | day            | `CharField(max_length=10)`             |                                                                                     |
|                                | start\_time    | `TimeField()`                          |                                                                                     |
|                                | lab\_time      | `BooleanField(default=False)`          |                                                                                     |
|                                |                | `__str__`                              | `"course (day - start_time)"`                                                       |
| **Match\_instructorANDcourse** | major          | `ManyToManyField(Major)`               | `blank=True`                                                                        |
|                                | classroom      | `ForeignKey(Classroom)`                | `related_name='main_class_matches'`, `on_delete=CASCADE`                            |
|                                | lab\_room      | `ForeignKey(Classroom)`                | `related_name='lab_class_matches'`, `null=True`, `blank=True`, `on_delete=CASCADE`  |
|                                | instructor     | `ForeignKey(User)`                     | `limit_choices_to={"groups__name": "Instructor"}`, `null=True`, `blank=True`        |
|                                | semester       | `ForeignKey(Semester)`                 | `on_delete=CASCADE`                                                                 |
|                                | course         | `ForeignKey(Course)`                   | `on_delete=CASCADE`                                                                 |
|                                |                | `Meta`                                 | `unique_together=('classroom','instructor','course','semester')`                    |
|                                |                | `__str__`                              | `"classroom - course by instructor (semester)"`                                     |
| **Company**                    | company\_name  | `CharField(max_length=100)`            |                                                                                     |
|                                | group\_count   | `IntegerField(default=0)`              |                                                                                     |
|                                |                | `__str__`                              | `company_name`                                                                      |
| **CompanyGroup**               | company        | `ForeignKey(Company)`                  | `on_delete=SET_NULL`, `null=True`, `blank=True`                                     |
|                                | name           | `CharField(max_length=50)`             |                                                                                     |
|                                | students       | `ManyToManyField(User)`                | `blank=True`, `related_name='student_groups'`                                       |
|                                | supervisor     | `ForeignKey(User)`                     | `on_delete=SET_NULL`, `null=True`, `blank=True`, `related_name='supervisor_groups'` |
|                                |                | `__str__`                              | `"name - company supervised by supervisor"`                                         |
| **Feedback**                   | user\_email    | `EmailField()`                         |                                                                                     |
|                                | feedback       | `TextField()`                          |                                                                                     |
|                                |                | `__str__`                              | `user_email`                                                                        |
| **Subscriber**                 | email          | `EmailField()`                         |                                                                                     |
|                                |                | `__str__`                              | `email`                                                                             |


