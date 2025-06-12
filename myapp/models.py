from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
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

class Feedback(models.Model):
    user_email = models.EmailField()
    feedback = models.TextField()

    def __str__(self):
        return self.user_email

class Subscriber(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

