# UCSY ClockWise ⏰

![Built with Django](https://img.shields.io/badge/Built%20With-Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Status](https://img.shields.io/badge/Project-In_Development-yellow?style=for-the-badge)


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
```

class Major(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Semester(models.Model):
    name = models.CharField(max_length=10, unique=True)  # Example: "1st Sem", "2nd Sem"

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)
    semester = models.ManyToManyField(Semester, blank=True)
    major = models.ManyToManyField(Major, blank=True)
    lab_required = models.BooleanField(default=False)
    credit_hours = models.IntegerField(null=True, blank=True)
    lab_hours = models.IntegerField(null=True, blank=True)
    lecture_hours = models.IntegerField(null=True, blank=True)
    instructors = models.ManyToManyField(User, blank=True)


    def __str__(self):
        return f"{self.course_id} ({self.name})"


class Classroom(models.Model):
    room_number = models.CharField(max_length=15, unique=True)
    majors = models.ManyToManyField(Major, blank=True)  # Many majors can use a classroom
    semesters = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)  # Many semesters can use a classroom
    instructors = models.ManyToManyField(User, blank=True)
    is_lab = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.room_number} - {', '.join(major.name for major in self.majors.all())}"

course_type = [
    ('elective','elective'),
    ('supporting','supporting'),
    ('general','general'),
    ('major','major')
]
class CourseSemesterInfo(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    semester = models.ForeignKey('Semester', on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=course_type, default='general')

    class Meta:
        unique_together = ('course', 'semester')

    def __str__(self):
        return f"{self.course.name} in {self.semester.name} as {self.type}"


class LabroomUsed(models.Model):
    lab_room = models.CharField(max_length=15)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    lab_hours = models.IntegerField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.lab_room

    def clean(self):
        """Check if this course in this room and semester already has a lab assigned."""
        if self.semester and self.room and self.course:
            exists = LabroomUsed.objects.filter(
                semester=self.semester,
                room=self.room,
                course=self.course
            ).exclude(id=self.id).exists()

            if exists:
                raise ValidationError(
                    f"Lab already assigned for course '{self.course}' in room '{self.room}' during semester '{self.semester}'."
                )

    def save(self, *args, **kwargs):
        self.clean()  # Perform custom validation
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    major = models.ForeignKey(Major,on_delete=models.SET_NULL,null=True, blank=True)
    within_Campus =  models.BooleanField(default=False)

    def str(self):
        return f"{self.user.username} - {self.department.name if self.department else 'No Department'}"

class Timetable_Schedule(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='main_class'  # 👈 distinguish this reverse relation
    )
    lab_room = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lab_matches'  # 👈 distinguish this reverse relation
    )
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    lab_time = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course.name} ({self.day} - {self.start_time})"

class Match_instructorANDcourse(models.Model):
    major = models.ManyToManyField(Major, blank=True)

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='main_class_matches'  # 👈 distinguish this reverse relation
    )

    lab_room = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lab_class_matches'  # 👈 distinguish this reverse relation
    )

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': "Instructor"}
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classroom', 'instructor', 'course', 'semester')

    def __str__(self):
        return f"{self.classroom} - {self.course} by {self.instructor} ({self.semester})"

class Company(models.Model):
    company_name = models.CharField(max_length=100)
    group_count = models.IntegerField(default=0)

    def __str__(self):
        return self.company_name

class CompanyGroup(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50)
    students = models.ManyToManyField(User, blank=True, related_name='student_groups')
    supervisor = models.ForeignKey(User, blank=True, related_name='supervisor_groups', on_delete=models.SET_NULL,
                                   null=True)

    def __str__(self):
        return f"{self.name} - {self.company} supervised by {self.supervisor}"


class Notice(models.Model):

    sender = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    tag = models.CharField(max_length=20)
    to_all = models.BooleanField(default=False)
    to_teacher = models.BooleanField(default=False)
    to_all_semesters = models.BooleanField(default=False)
    to_classrooms = models.ManyToManyField(Classroom ,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ReadStatus(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.notice.title

class Feedback(models.Model):
    user_email = models.EmailField()
    feedback = models.TextField()

    def __str__(self):
        return self.user_email

class Subscriber(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


```
