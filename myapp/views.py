import ast
import datetime
from datetime import datetime, time, timedelta
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_time

from .forms import CustomPasswordChangeForm
from .models import Major, Classroom, CourseSemesterInfo,Course, Department, Semester, Timetable_Schedule,CompanyGroup, Company, Feedback, Subscriber,Match_instructorANDcourse,LabroomUsed
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
import itertools  # ✅ Used for cycling throCSugh instructors
from collections import defaultdict, Counter
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
import json

def loginForm(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            print(user)
            print(email, password)
            if user.is_superuser:
                return redirect('/admin_home/')

            elif user.groups.filter(name='Instructor').exists():
                request.session["role"] = "Instructor"
                return redirect('/viewPage/')

            elif user.groups.filter(name="Student").exists():
                request.session["role"] = "Student"
                return redirect('/viewPage/')

        else:
            messages.error(request,"Invalid credentials. Please try again.")

    return render(request, "login.html")


@login_required
def user_account(request):
    if request.method=='POST':
        form = CustomPasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            user =form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password successfully changed!")
            return redirect("/account/")
        else:
            messages.error(request, "Error updating password. Please try again.")

    else:
        form= CustomPasswordChangeForm(request.user)
        return render(request, 'account.html', {'form': form})


@login_required
def logOut(request):
    logout(request)
    return redirect('/login')


def is_in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_home(request):
    feedbacks= Feedback.objects.all()
    feedback_list = []
    for feedback in feedbacks:
        user = User.objects.filter(email=feedback.user_email).first()
        feedback.first_name = user.first_name if user else "Anonymous"  # Add first_name attribute
        feedback_list.append(feedback)
    request.session["role"] = "Admin"
    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Identify which form was submitted


        if form_type == "subscribe":
            email = request.POST.get("email")
            if email:
                Subscriber.objects.create(email=email)
                messages.success(request, "You are subscribed! We will remind you.")
                return redirect("/admin_home/")


        elif form_type == "feedback":
            user_email = request.POST.get('user_email')
            feedback_text = request.POST.get("feedback")
            if feedback_text:
                user = User.objects.filter(email=user_email).first()
                first_name = user.first_name if user else "Anonymous"

                Feedback.objects.create(user_email=user_email, feedback=feedback_text)
                messages.success(request, f"Thank you for your feedback, {first_name}!")
                return redirect("/admin_home/")

    return render(request, "home.html", {"feedbacks": feedback_list})


@login_required
@user_passes_test(lambda u: is_in_group(u, "Instructor") or is_in_group(u,"Student"))
def viewPage(request):
    feedbacks = Feedback.objects.all()
    feedback_list = []
    for feedback in feedbacks:
        user = User.objects.filter(email=feedback.user_email).first()
        feedback.first_name = user.first_name if user else "Anonymous"  # Add first_name attribute
        feedback_list.append(feedback)
    print(feedbacks)
    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Identify which form was submitted

        if form_type == "subscribe":
            email = request.POST.get("email")
            if email:
                Subscriber.objects.create(email=email)
                messages.success(request, "You are subscribed! We will remind you.")
                return redirect("/viewPage/")
        elif form_type == "feedback":
            user_email = request.POST.get('user_email')
            feedback_text = request.POST.get("feedback")
            if feedback_text:
                user = User.objects.filter(email=user_email).first()
                first_name = user.first_name if user else "Anonymous"
                Feedback.objects.create(user_email=user_email, feedback=feedback_text)
                messages.success(request, f"Thank you for your feedback, {first_name}!")
                return redirect("/viewPage/")

    return render(request, 'viewPage.html', {'feedbacks': feedback_list})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def select_semester(request):
    if request.method == "POST":
        semester = request.POST.get("semester")
        request.session["semester"] = semester
        semester_name = Semester.objects.get(id=semester)
        if semester_name.name.lower() == 'Semester10'.lower():
            return redirect('/assign_groups/')
        else:
            return redirect("/fill_room_data")
    else:
        semester = Semester.objects.all()
        return render(request, "index.html", {'sem': semester})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def assign_groups(request):
    if request.method == "POST":
        companies = Company.objects.all()
        groups = CompanyGroup.objects.all()

        selected_groups = {}
        for company in companies:
            selected_groups[company.id] = request.POST.getlist(f'group_{company.id}')

        for company_id, group_ids in selected_groups.items():
            company = Company.objects.get(id=company_id)
            for group_id in group_ids:
                group = CompanyGroup.objects.get(id=group_id)
                group.company = company

                eligible_instructors = User.objects.filter(
                    groups__name="Instructor",
                    userprofile__department__name__in=["ITSM", "NLP", "Hardware", "SE"]
                )

                available_instructors = [
                    instructor for instructor in eligible_instructors
                    if instructor.supervisor_groups.count() < 2
                ]

                if available_instructors:
                    random_instructor = random.choice(available_instructors)
                    group.supervisor = random_instructor
                    group.save()

        company_groups = CompanyGroup.objects.all()
        return render(request, "groups.html", {'company_groups': company_groups})

    else:
        companies = Company.objects.all()
        groups = CompanyGroup.objects.all()
        print(companies)
        print(groups)
        return render(request, 'assign_groups.html', {'companies': companies, 'groups': groups})

@login_required
@user_passes_test(lambda u: is_in_group(u,"Student"))
def semester_ten(request):

    user = request.user
    company_group = CompanyGroup.objects.get(students=user)
    students = company_group.students.all()
    supervisor = company_group.supervisor

    return render(request, 'semester_ten.html', {
        'company_group': company_group,
        'students': students,
        'supervisor': supervisor,
        'user': user
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_admin(request):
    if request.method == "POST":
        print("HELLO")
        semester = request.POST.get("semester")
        semester_name = Semester.objects.get(id=semester)
        if semester_name.name.lower() == 'Semester10'.lower():
            company_groups = CompanyGroup.objects.all()
            print(company_groups)
            return render(request, "groups.html", {'company_groups': company_groups})
        else:
            return redirect(f"/timetable_list/{semester}")

    else:
        semester = Semester.objects.all()
        return render(request, "view.html", {'sem': semester})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def timetable_list(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    rooms = Timetable_Schedule.objects.filter(semester=semester).values_list('classroom', flat=True).distinct()
    classrooms = Classroom.objects.filter(id__in=rooms)

    return render(request, 'timetable_list.html', {
        'classrooms': classrooms,
        'semester_id': semester_id
    })


@login_required()
def home(request):
    return render(request, "home.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def view(request):
    if request.method == "POST":
        semester = request.POST.get("semester")
        return redirect(f"/timetable_list/{semester}")
    else:
        semester = Semester.objects.all()
        return render(request, "view.html", {'sem': semester})


def display_timetable(semester):
    classrooms = Timetable_Schedule.objects.get(semester=semester)
    print("Classrooms:", classrooms)
    Timetables = []
    timetable = []
    for classroom in classrooms:
        timetable.append(Timetable_Schedule.objects.filter(classroom=classroom))
        Timetables.append(timetable)


def get_instructors(request):
    dept_name = request.GET.get("department_name")
    print("Select department:", dept_name)
    instructor_group = Group.objects.get(name="Instructor")
    print("Group Name:", instructor_group)
    instructors = User.objects.filter(groups=instructor_group, userprofile__department__name=dept_name)

    instructor_list = []
    for i in instructors:
        count = 0
        print("\nCurrent instructor :", i.first_name)
        slots = Timetable_Schedule.objects.filter(instructor=i).values('start_time')
        for s in slots:
            count += 1
        print("\nCount slot: ",count)
        if count < 6:
            instructor_list.append(
                {
                    "id": i.id,
                    "first_name": i.first_name,
                }
            )
        else:
            print("\nSkip ", i.first_name)
            continue

    print("Fetched Instructors:", instructor_list)
    # Returning as a JsonResponse for easy handling in frontend (AJAX or similar)
    return JsonResponse({"instructors": instructor_list})


def showlist(request):
    courses = Course.objects.filter(semester="6")
    return render(request, "mapping_success.html", {"courses": courses})


def classroom_timetable(request, semester_id):
    print("\nClassroom timetable function is starting")
    semester = Semester.objects.get(id=semester_id)
    print("\nSemester :", semester)
    classrooms = []
    course_instructor_list = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slot = ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "Break Time", "1:00 - 2:00", "2:00 - 3:00",
            "3:00 - 4:00"]  # Example time slots
    start_times = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]
    classrooms_set = Timetable_Schedule.objects.filter(semester=semester).values('classroom')
    print("\nClassrooms:", classrooms_set)
    temp = None

    for classroom in classrooms_set:
        id = classroom['classroom']
        if id == temp:
            continue
        classroom = Classroom.objects.get(id=id)
        room_info = {
            'classroom': {'id': classroom.id,
                          'room_number': classroom.room_number,
                          'majors': [major.name for major in classroom.majors.all()]},
            'schedule': []
        }
        print("\nRoom info:", room_info)

        course_instructor = Timetable_Schedule.objects.filter(classroom=room_info['classroom']['id']).values('course',
                                                                                                             'instructor')
        print("\nCourse_instructor: ", course_instructor)
        unique_courses = set()

        for ci in course_instructor:
            course_name = Course.objects.filter(id=ci['course']).values_list('name', flat=True).first() or ''
            instructor_name = User.objects.filter(id=ci['instructor']).values_list('first_name',
                                                                                   flat=True).first() or ''

            # Create a tuple of (course_name, instructor_name) to check uniqueness
            course_tuple = (course_name, instructor_name)
            print("\nCourse_name :", course_name)
            if course_tuple not in unique_courses:
                unique_courses.add(course_tuple)  # Add to set to avoid duplicates
                course_instructor_list.append({
                    'course_name': course_name,
                    'instructor_name': instructor_name,
                    'classroom': room_info['classroom']
                })

        temp = id
        for day in days:
            # Note: each course include instructor and start_time at timetable
            day_course = {
                'day': day,
                'courses': [],
            }
            courses = Timetable_Schedule.objects.filter(classroom=id, semester=semester, day=day).values('course',
                                                                                                         'instructor',
                                                                                                         'start_time').order_by(
                'start_time')
            course_tem = []
            print("\nCourses:", courses)
            for time in start_times:
                time_obj = datetime.strptime(time, "%H:%M").time()  # Convert string time to time object
                slot_courses = []  # Store courses for the same time slot

                for course_data in courses:
                    if time_obj == course_data['start_time']:  # Check if course exists for this time slot
                        course_entry = {
                            'course_name': Course.objects.filter(id=course_data['course']).values_list('name',
                                                                                                       flat=True).first() or '',
                            'instructor': User.objects.filter(id=course_data['instructor']).values_list('first_name',
                                                                                                        flat=True).first() or '',
                            'start_time': str(course_data['start_time']),  # Convert to string for consistency
                        }
                        slot_courses.append(course_entry)  # Add course to the slot list

                    # If multiple courses exist in the same time slot, replace them with a single "Electives" entry
                print("Time", time)
                if len(slot_courses) > 1:
                    course_names = '/'.join([course['course_name'] for course in slot_courses])
                    course_entry = {
                        'course_name': course_names,
                        'instructor': '',
                        'start_time': str(time),
                    }
                elif slot_courses:
                    course_entry = slot_courses[0]  # If only one course exists, use it
                else:
                    course_entry = {
                        'course_name': ' ',
                        'instructor': '',
                        'start_time': str(time),
                    }

                print("Course:", course_entry)
                day_course['courses'].append(course_entry)

            room_info['schedule'].append(day_course)
        classrooms.append(room_info)

    print("\nClassrooms:", classrooms)
    print("\n", type(classrooms))
    return render(request, 'timetable2.html',
                  {'classrooms': classrooms, 'start_times': slot, 'instructors': course_instructor_list})


def test(request):
    return redirect(f'/timetable/{3}/')


@login_required
@user_passes_test(lambda u: is_in_group(u, "Instructor"))
def teacherTest(request, pk):
    return redirect(f'/teacher_view/{pk}/')

# this is for administrator generating role''s functions


# this is for administrator generating role''s functions

@login_required()
def choose_semester(request):
    if request.method == "POST":
        semester = request.POST.get("semester")
        request.session["semester"] = semester  # Store in session
        return redirect("/fill_room_data")  # Redirect to room input page
    else:
        semester = Semester.objects.all()
        return render(request, "index.html", {'sem': semester})

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def fill_rooms(request,semester_id):

    scheduled_classrooms = Match_instructorANDcourse.objects.values_list('classroom', flat=True)
    classrooms = Classroom.objects.exclude(id__in=scheduled_classrooms).filter(is_lab=False)
    print("\nClassrooms that need to display.\n",classrooms)
    if not semester_id:
        return redirect("/choose_semester")
    try:
        semester = Semester.objects.get(id=semester_id)
        print("Semester:",semester)
    except Semester.DoesNotExist:
        return redirect("/choose_semester")
    majors = Major.objects.all()
    print("Majors that need to display:\n",majors)

    if request.method == "POST":
        # Count how many rooms were sent
        num_rooms = len([key for key in request.POST.keys() if key.startswith('room_number_')])
        print("\nNumber of rooms:",num_rooms)

        all_data = []

        for i in range(num_rooms):
            room_number = request.POST.get(f'room_number_{i}')
            major_ids = request.POST.getlist(f'major_{i}[]')  # Important: use getlist()

            if room_number:
                # You can save to database or just collect
                room_data = {
                    'room_number': room_number,
                    'majors': major_ids,  # list of selected major IDs
                }
                all_data.append(room_data)

                print(f"Room {i}: {room_number}")
                print(f"Majors selected: {major_ids}")

        # Example: you can store into session or process directly
        request.session['all_data'] = all_data
        request.session["semester"] = semester_id
        print("All_data")

        print("\nPOST request sent")
        return redirect('/assign_instructors')

    return render(request, "fillroom.html",{"semester": semester, "majors":majors, "classrooms": classrooms})


def get_instructors(request):

    #Only show instructors who have 20 slots or less than 20 including new credit slots

    dept_name = request.GET.get("department_name")
    print("Select department:", dept_name)

    credit_hours = request.GET.get("credit_hours")
    print("Credit hours:", credit_hours)

    instructor_group = Group.objects.get(name="Instructor")
    print("Group Name:", instructor_group)
    instructors = User.objects.filter(groups=instructor_group, userprofile__department__name=dept_name)

    instructors_list =[]
    for i in instructors:
        unique_slot_count = (
            Timetable_Schedule.objects
            .filter(instructor=i)
            .values('day', 'start_time')
            .distinct()
            .count()
        )
        print(f"Total scheduled classes for instructor: {unique_slot_count}")
        if unique_slot_count+int(credit_hours) <= 20:
            instructor_data = {
                'id': i.id,
                'first_name': i.first_name
            }
            instructors_list.append(instructor_data)
        else:
            continue

    return JsonResponse({'instructors': instructors_list})

def get_available_labs(request):

    credit_hours = request.GET.get('credit_hours')
    print("Credit hours for lab:", credit_hours)

    course_id = request.GET.get('course_id')

    if not credit_hours:
        return JsonResponse({'labs': []})

    credit_hours = int(credit_hours)

    # Filter labs based on your logic — for example:
    # Only labs that are not overbooked
    labs = Classroom.objects.filter(is_lab=True)

    available_labs = []
    for lab in labs:
        lab_usage = (
            Timetable_Schedule.objects
            .filter(lab_room=lab)
            .values('day', 'start_time')
            .distinct()
            .count()
        )
        if lab_usage + credit_hours <= 20:
            print("Lab name:", lab.room_number)
            available_labs.append({'room_number': lab.room_number})

    return JsonResponse({'labs': available_labs})


@login_required()
def assign_instructors(request):
    print("\nStarting assign instructor and lab room")
    semester_id = request.session.get("semester")
    departments = Department.objects.all()

    room_data = request.session.get("all_data", [])

    print("\nSelected semester id:", semester_id)
    print("\nRoom data:", room_data)

    #function call to update majors and semester data to each selected classroom
    assgin_majorsAndsemester_to_classroom(room_data,semester_id)
    rooms = []
    selected_majorIDs =[]

    for room in room_data:
        print("\n")
        print("Room", room['room_number'])
        major_ids = room.get('majors', [])  # list of major ids
        print("major_ids", major_ids)
        selected_majorIDs.extend(major_ids)  # flatten the list
        majors = Major.objects.filter(id__in=major_ids)
        print("Major:", majors)

        # Get the courses related to the majors
        courses = Course.objects.filter(
            semester__id=semester_id,
            major__id__in=selected_majorIDs
        ).distinct()

        print("Courses:", courses)

        coursesperroom = Course.objects.filter(
            semester__id= semester_id,
            major__id__in= major_ids
        )
        unique_courses = {}
        for c in coursesperroom:
            info = CourseSemesterInfo.objects.filter(course=c, semester=Semester.objects.get(id=semester_id)).first()
            type = info.type
            if c.course_id not in unique_courses:
                unique_courses[c.course_id] = {
                    "course_id": c.course_id,
                    "name": c.name,
                    "type": type
                }

        # Prepare the each_room dictionary with courses
        each_room = {
            'room_number': room['room_number'],
            'majors': [{"id": m.id, "name": m.name} for m in majors],
            'courses': list(unique_courses.values())
        }

        print("Each Room:", each_room['room_number'])
        print("majors:", each_room['majors'])
        print("Course:", each_room['courses'])
        rooms.append(each_room)

    print("\nSelected Courses:")
    for c in courses:
        print(f"Course Name: {c.name}")
        print(f"Major Ids: {[m.id for m in c.major.all()]}")
        print(f"Lab Information:{c.lab_required}")

    labrooms = Classroom.objects.filter(is_lab=True)

    if request.method == "POST":
        print("\nPost request sent")

        if request.method == 'POST':
            course_data = []  # Fixed: make it a list

            for course in courses:
                print("\nCourse:", course.course_id)
                course_id = course.course_id

                credit_hours = request.POST.get(f'credit_hours_{course_id}')
                department_name = request.POST.get(f"department_{course_id}", "")

                lab_credit_hours = None
                lab_room = None
                lecture_hours = 0
                if course.lab_required:
                    print("This course need lab", course.course_id)
                    lab_credit_hours = request.POST.get(f'lab_credit_hours_{course_id}')
                    lecture_hours = int(credit_hours) - int(lab_credit_hours)
                    lab_hours = lab_credit_hours

                    for room in rooms:
                        for c in room['courses']:
                            if c['course_id'] == course.course_id:
                                lab_room = request.POST.get(f'lab_{course.course_id}_{room["room_number"]}')
                                print(f"Room: {room['room_number']}, Selected Lab: {lab_room}")
                                selected_classroom = Classroom.objects.get(room_number=room['room_number'])
                                semester = Semester.objects.get(name=selected_classroom.semesters)
                                lab_hours = lab_credit_hours
                                new_lab_used = LabroomUsed.objects.create(
                                    lab_room=lab_room,
                                    semester=semester,
                                    room=selected_classroom,
                                    lab_hours=lab_hours,
                                    course=course
                                )
                                print("New lab used:", new_lab_used)

                else:
                    lecture_hours = credit_hours

                for room in rooms:
                    print("Room_number:", room['room_number'])
                    room_number = room["room_number"]
                    key = f'instructors_{course_id}_{room_number}'
                    instructor_id = request.POST.get(key)
                    print(f"Key: {key}, Instructor id: {instructor_id}")

                    if not instructor_id:
                        print(f"❗ No instructor selected for course {course_id} in room {room_number}")
                        continue

                    try:
                        instructor = User.objects.get(id=instructor_id)
                        classroom = Classroom.objects.get(room_number=room_number)
                        co = Course.objects.get(course_id=course_id)
                        semester = Semester.objects.get(id=semester_id)

                        match = Match_instructorANDcourse.objects.create(
                            classroom=classroom,
                            course=co,
                            instructor=instructor,
                            semester=semester,
                        )
                        match.major.set(classroom.majors.all())
                        print("✅ Match saved:", match)

                    except User.DoesNotExist:
                        print(f"❌ Instructor with id {instructor_id} not found.")
                    except Exception as e:
                        print(f"❌ Error saving match: {e}")

                    for room in rooms:
                        room_courses = [c['course_id'] for c in room['courses']]
                        if course_id in room_courses:
                            course_data_item = {
                                "course_id": course.course_id,
                                "name": course.name,
                                "credit_hours": credit_hours,
                                "lab_credit_hours": lab_credit_hours,
                                "lecture_hours": lecture_hours,
                                "department": department_name,
                                "room_number": room['room_number'],
                                "instructors": [
                                    {"id": instructor.id, "username": instructor.username}
                                ]
                            }

                        # Append the data to course_data list
                        course_data.append(course_data_item)
                        update_course_from_dict(course_data_item)  # Updating required data of each course

        request.session["courses"] = course_data
        request.session.modified = True

        room_data_list = collectForEachRoom(rooms, semester_id)  # collect one room's data complectly to generate
        scheduling(room_data_list, semester_id)  # calling the generate functions
        return redirect(reverse('timetable_list', args=[semester_id]))

    return render(request, "assign_instructor.html", {
        "departments": departments,
        "courses": courses,
        "labs": labrooms,
        "rooms": rooms,
        "semester": Semester.objects.filter(id=semester_id),
    })


def assgin_majorsAndsemester_to_classroom(room_data,semester_id):
    print("\nStarting the assigning the selected majors and semester to related classrooms.\n")
    for r in room_data:
        print("Current classroom is ", r['room_number'])
        current_semester = Semester.objects.get(id=semester_id)
        room_number = r['room_number']
        majors_ids = r['majors']

        classroom = Classroom.objects.get(room_number=room_number)

        majors = Major.objects.filter(id__in=majors_ids)

        classroom.majors.set(majors)
        print("majors",majors)
        print("successfully set majors to classroom.")
        classroom.semesters = current_semester
        print("successfully set semester to classroom.")
        classroom.save()
        print("Successfully save the majors to the classroom:", r['room_number'])
        print("-------------")

def update_course_from_dict(course_data_item):
    # 1) Fetch the Course instance (or 404 / handle DoesNotExist)
    course = get_object_or_404(Course, course_id=course_data_item['course_id'])

    course.credit_hours  = course_data_item.get('credit_hours')
    course.lab_hours     = course_data_item.get('lab_credit_hours')
    course.lecture_hours = course_data_item.get('lecture_hours')

    # 3) Save before touching M2M relations
    course.save()

    # 4) Update many-to-many: instructors
    instructor_ids = [i['id'] for i in course_data_item.get('instructors', [])]
    if instructor_ids:
        users_qs = User.objects.filter(id__in=instructor_ids)
        course.instructors.set(users_qs)

def collectForEachRoom(rooms,semester_id):
    print("\nThis fuction is to collect each room data completely but only each ID")
    room_data_list = []
    semester = Semester.objects.get(id=semester_id)

    for r in rooms:
        # 1) Lookup the Classroom by its room_number
        cls = Classroom.objects.get(room_number=r['room_number'])
        r_id = cls.id
        print("\nRoom:",cls)
        print("Semester:",semester)

        # 2) Pull out the majors (by id)
        major_ids = list(cls.majors.values_list('id', flat=True))
        print("majors:",major_ids)

        # 3) Build the courses list
        courses_list = []
        for cinfo in r['courses']:
            course = Course.objects.get(course_id=cinfo['course_id'])
            classroom_majors = set(cls.majors.all())
            course_majors = set(course.major.all())

            # 🚫 Skip if course majors and classroom majors don't overlap
            if not classroom_majors & course_majors:
                print(f"⚠️ Skipping course '{course.name}' for room {cls.room_number}: not part of its majors.\n-----")
                continue
            print("Course:",course)
            try:
                ins = Match_instructorANDcourse.objects.get(
                    course=course,
                    classroom=cls,
                    semester=semester
                )
                print("Instructor:", ins.instructor.first_name)
            except Match_instructorANDcourse.DoesNotExist:
                print(f"No match found for course {course}, classroom {cls}, semester {semester}")
            instructor_id = ins.instructor.id

            if course.lab_required == True:
                l_r = LabroomUsed.objects.get(room=cls,semester=semester,course=course)
                l_r_number = Classroom.objects.get(room_number=l_r)
                print("Lab room number:",l_r_number)
                lab_id = l_r_number.id
            else:
                lab_id = None
            courses_list.append({
                'course_id': course.id,
                'lab_id': lab_id,
                'instructor_id': instructor_id
            })
            print("----")

        # 4) Assemble this room’s dict
        room_data_list.append({
            'room_id': r_id,
            'majors': major_ids,
            'courses': courses_list,
        })
    return room_data_list

def scheduling(room_data_list, semester_id):
    print("\nStart scheduling:")

    for room in room_data_list:
        elective=[]
        supporting = []
        rooms = []

        cls = Classroom.objects.get(id=room['room_id'])
        sem = Semester.objects.get(id=semester_id)
        print("-----\nStart scheduling for ",cls," of ",sem,".\n")

        for c in room['courses']:
            cou = Course.objects.get(id=c['course_id'])
            info = CourseSemesterInfo.objects.get(course=cou, semester=sem)
            print(info.type)
            print("Course:",cou)
            if info.type in ['general', 'major']:
                #print("This is ", cou.type," type.")
                firstTypeSchedule(c,room['room_id'],semester_id) #calling the fuction for scheduling course types general and major.
            elif info.type in ['elective']:
                #print("This is ", cou.type," type.")
                elective.append(c)
            elif info.type in ['supporting']:
                #print("This is ", cou.type, " type.")
                supporting.append(c)
            else:
                print("Invalid type.")

        if elective:
            flag = secondTypeSchedule(elective, room['room_id'], semester_id) #calling the function for scheduling courses which type elective
            if flag == True:
                print("\nSuccessfully scheduled all elective courses")

        if supporting:
            flag = secondTypeSchedule(supporting, room['room_id'], semester_id) #calling the function for scheduling courses which type supporitng
            if flag == True:
                print("\nSuccessfully scheduled all supporting courses.")


def firstTypeSchedule(c,room_id,semester_id):
    print("\nThis is first type scheduling.")

    cls = Classroom.objects.get(id= room_id)
    sem = Semester.objects.get(id= semester_id)
    cou = Course.objects.get(id=c['course_id'])
    print("Current course:", cou.course_id)
    instructor = User.objects.get(id=c['instructor_id'])
    credits_hours = cou.credit_hours

    assigned_hours = 0

    if cou.lab_required:
        print("Course require lab")
        lab_room = Classroom.objects.get(id=c['lab_id'])
        print("Lab:",lab_room)
        lab_hours = cou.lab_hours
        lecture_hours = cou.lecture_hours

        # 💡 Divide into 2-hour sessions (each 2 slots), schedule lab first
        if create_slot_objects(cls, sem, instructor, cou, lab_room, lab_hours):
            assigned_hours += lab_hours

        if lecture_hours:
            lab_room = None
            if create_slot_objects(cls, sem, instructor, cou, lab_room, lecture_hours):
                assigned_hours += lecture_hours
    else:
        lab_room = None
        credit_hours = cou.credit_hours
        if create_slot_objects(cls, sem, instructor, cou, lab_room, credit_hours):
            assigned_hours += credit_hours

    if assigned_hours == credits_hours:
        print("Successfully generate for ", cou.name, " of ", cls.room_number)
    else:
        print("Fail to scheduled")

def create_slot_objects(cls, sem, instructor, cou, lab_room, hours):
    print("\n🛠 Creating Timetable_Schedule objects")
    scheduled_hours = 0
    total_hours = hours

    # Try assigning as many 2-hour blocks as possible
    used_days = set()

    while scheduled_hours + 2 <= total_hours:
        day, t1, t2 = take_two_free_slots(cls, sem, instructor, cou, lab_room, exclude_days=used_days)
        if day and t1 and t2:
            for t in [t1, t2]:
                Timetable_Schedule.objects.create(
                    semester=sem,
                    course=cou,
                    instructor=instructor,
                    classroom=cls,
                    lab_room=lab_room,
                    day=day,
                    start_time=t
                )
            print(f"✅ Scheduled 2-hour block on {day} at {t1} & {t2}")
            scheduled_hours += 2
            used_days.add(day)  # Move to next day next time
        else:
            print("⚠️ No 2-hour slots available, switching to 1-hour allocation")
            break  # Exit and fallback to 1-hour assignment

    # Assign remaining hours using single slots
    while scheduled_hours < total_hours:
        day, slot = find_random_single_slot(cls, sem, instructor, lab_room, cou)
        if day and slot:
            Timetable_Schedule.objects.create(
                semester=sem,
                course=cou,
                instructor=instructor,
                classroom=cls,
                lab_room=lab_room,
                day=day,
                start_time=slot
            )
            print(f"🟡 Scheduled 1-hour slot on {day} at {slot}")
            scheduled_hours += 1
            used_days.add(day)
        else:
            print("❌ Failed to schedule remaining 1-hour slot")
            break  # Prevent infinite loop if no slots left

    if scheduled_hours == hours: True
    else: False

def pick_random_day(days, exclude_days):
    available_days = [d for d in days if d not in exclude_days]
    if not available_days:
        return None  # no days left to pick
    return random.choice(available_days)

def is_there_same_course(day, room, course):
    print("Checking is there same course schedule exit")

    same_course_schedule = Timetable_Schedule.objects.filter(
        classroom = room,
        day = day,
        course = course
    ).exists()

    return same_course_schedule


def take_two_free_slots(room, semester, instructor, course, lab_room, exclude_days):
    print("\n🔍 Searching for 2 free consecutive slots")

    slots = [time(hour) for hour in range(9, 12)] + [time(hour) for hour in range(13, 15)]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    max_attempts = 20
    attempt = 0
    fallback_result = None

    profile = getattr(instructor, 'userprofile', None)
    is_off_campus = profile and not profile.within_Campus

    for day in days:
        same_course_schedule = is_there_same_course(day, room, course)
        if same_course_schedule:
            continue

        while attempt < max_attempts:
            attempt += 1

            slot1,slot2 = get_random_consecutive_slots(slots)

            if not slot1 or not slot2:
                continue

            is_valid = is_valid_slots(day, slot1, slot2, room, semester, instructor, course, lab_room)

            if not is_valid:
                print(f"Conflict at {slot1}-{slot2}, trying next....")
                continue

            if is_off_campus and (slot1 == time(9, 0) or slot2 == time(15, 0)):
                print(f"⚠️ Valid slot, but off-campus instructor cannot teach at edge hours. Storing fallback.")
                if not fallback_result:
                    fallback_result = (day, slot1, slot2)
                continue

            print(f"✅ Valid slot found: {day} {slot1}–{slot2}")
            return day, slot1, slot2

    # Try fallback if available
    if fallback_result:
        fallback_day, fallback_t1, fallback_t2 = fallback_result
        print("⚠️ Using fallback slot due to lack of better options...")
        return fallback_day, fallback_t1, fallback_t2

    print("❌ No available slot pair found after max attempts.")
    return None, None, None

def find_random_single_slot(classroom, semester, instructor, lab_room, cou):
    print("🔍 Searching for 1 free slot")
    slots = [time(hour) for hour in range(9, 12)] + [time(hour) for hour in range(13, 15)]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    max_attempts = 20
    attempt = 0
    fallback = None

    profile = getattr(instructor, 'userprofile', None)
    is_off_campus = profile and not profile.within_Campus

    for day in days:

        is_same_course_schedule = is_there_same_course(day, classroom, cou)
        if is_same_course_schedule:
            continue

        while attempt < max_attempts:
            attempt += 1
            slot = random.choice(slots)

            #Check for conflicts first
            conflict = Timetable_Schedule.objects.filter(
                semester = semester,
                classroom = classroom,
                day = day,
                start_time = slot
            )

            if conflict:
                continue

            instructor_busy = Timetable_Schedule.objects.filter(
                instructor = instructor,
                day = day,
                start_time = slot
            ).exists()

            if instructor_busy:
                continue

            if  lab_room:
                lab_busy = Timetable_Schedule.objects.filter(
                    lab_room = lab_room,
                    day = day,
                    start_time = slot
                ).exists()

                if lab_busy:
                    continue

            if is_off_campus and (slot == time(9, 0) or slot == time(15, 0)):
                if not fallback:
                    print(f"⚠️ Edge-hour slot {slot} for off-campus instructor, storing fallback.")
                    fallback = (day, slot)
                continue

            print(f"✅ Found good slot: {day} {slot}")
            return day, slot

    if fallback:
        print(f"⚠️ Using fallback: {fallback[0]} {fallback[1]}")
        return fallback

    print("❌ No free 1-hour slot found")
    return None, None

def get_random_consecutive_slots(slots):
    sorted_slots = sorted(slots)
    valid_pairs = []

    for i in range(len(sorted_slots) - 1):
        first, second = sorted_slots[i], sorted_slots[i + 1]

        # 💡 Skip pairs that cross lunch break (11 -> 13)
        if first == time(11) and second == time(13):
            continue

        # Only include truly 1-hour apart slots
        if (second.hour * 60 + second.minute) - (first.hour * 60 + first.minute) == 60:
            valid_pairs.append((first, second))

    return random.choice(valid_pairs) if valid_pairs else (None, None)


def is_valid_slots(day, slot1, slot2, room, semester, instructor, course, lab_room):
    # 💡 Conflict check for two slots
    conflicts = Timetable_Schedule.objects.filter(
        classroom = room,
        day = day,
        start_time__in = [slot1,slot2]
    )

    if conflicts.exists():
        return False

    instructor_busy = Timetable_Schedule.objects.filter(
        instructor = instructor,
        day = day,
        start_time__in = [slot1,slot2]
    ).exists()

    if instructor_busy:
        return False

    if lab_room:
        lab_busy = Timetable_Schedule.objects.filter(
            lab_room = lab_room,
            day = day,
            start_time__in = [slot1, slot2]
        ).exists()

        if lab_busy:
            return False

    # 💡 Check 3-continuous-hour constraint for instructor
    existing_slots = Timetable_Schedule.objects.filter(
        semester=semester,
        instructor=instructor,
        day=day
    ).values_list('start_time', flat=True)

    all_slots = list(existing_slots) + [slot1, slot2]
    clean_slots = [s for s in all_slots if isinstance(s, time)]
    slot_minutes = sorted([s.hour * 60 + s.minute for s in clean_slots])

    for i in range(len(slot_minutes) - 2):
        if slot_minutes[i + 1] == slot_minutes[i] + 60 and slot_minutes[i + 2] == slot_minutes[i] + 120:
            return False  # 🛑 Instructor already has 2+ consecutive hours

    return True

def secondTypeSchedule(course_list, rooms, semester_id):
    print("\nThis is second type scheduling.")

    cls = Classroom.objects.get(id=rooms)
    sem = Semester.objects.get(id=semester_id)
    cou_list = []
    for c in course_list:
        cou = {
         'course': Course.objects.get(id=c['course_id']),
         'instructor': User.objects.get(id=c['instructor_id'])
        }
        if c['lab_id'] == None:
            cou['lab'] = None
        else:
            cou['lab'] = Classroom.objects.get(id=c['lab_id'])
        cou_list.append(cou)

    free_slots, continuous_slots = findSlots(cls, sem, cou_list)

    credit_equal = checkCredithours(cou_list)
    if credit_equal ==True:
        print("All courses have the same credit hours.")

    assigned = scheduled_courses(cls, sem, cou_list, continuous_slots, free_slots)
    if assigned == True:
        print("Successfully assigned all courses.")
        return True
    else:
        print("Fail to assign all courses.")
        return False

def findSlots(cls, sem, cou_list):
    print("\n🔍 Finding all possible and continuous slots for elective/supporting courses")
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    slots = [time(hour) for hour in range(9, 12)] + [time(hour) for hour in range(13, 16)]

    free_slots = []
    free_continuous_slots = []

    # Step 1: Find all single shared free slots
    for day in days:
        for slot in slots:
            all_ok = True
            for c in cou_list:
                instructor = c['instructor']
                lab_room = c['lab']
                slot_conflict = is_time_slot_conflicted(sem, day, slot, cls, lab_room, instructor) #True လာရင် conflict , False လာရင် nonconflict
                if slot_conflict:
                    all_ok = False
                    break
            if all_ok:
                free_slots.append({
                    'day': day,
                    'slot': slot
                })

    # Step 2: Find non-overlapping continuous pairs from free_slots
    used_slots = set()  # Track which slots have been used in pairs

    for day in days:
        # Get and sort all free slots for the current day
        day_slots = sorted([s['slot'] for s in free_slots if s['day'] == day])

        i = 0
        while i < len(day_slots) - 1:
            s1 = day_slots[i]
            s2 = day_slots[i + 1]

            if (timedelta(hours=s2.hour) - timedelta(hours=s1.hour)) == timedelta(hours=1):
                free_continuous_slots.append({
                    'day': day,
                    'slots': [s1, s2]
                })
                # Mark both slots as used
                used_slots.add((day, s1))
                used_slots.add((day, s2))
                i += 2
            else:
                i += 1

    # Remove used slots from free_slots
    free_slots = [s for s in free_slots if (s['day'], s['slot']) not in used_slots]

    print("free slots",free_slots)
    print("\ncontinuous slots",free_continuous_slots)
    return free_slots, free_continuous_slots

def is_time_slot_conflicted(sem, day, slot, classroom, lab_room, instructor):

    conflict = Timetable_Schedule.objects.filter(
        day=day, start_time=slot
    ).filter(
        Q(classroom=classroom) | Q(instructor=instructor) | Q(lab_room=lab_room)
    ).exists()

    if conflict:
        return True
    else:
        return False

def checkCredithours(cou_list):
    # Extract credit hours from all courses in cou_list
    credit_hours_list = [cou['course'].credit_hours for cou in cou_list]

    # Check if all credit hours are the same
    all_same = len(set(credit_hours_list)) == 1

    if all_same:
        print("✅ All courses have the same credit hours:", credit_hours_list[0])
        return True
    else:
        print("❌ Courses have different credit hours:", credit_hours_list)
        return False

def scheduled_courses(cls, sem, cou_list, continuous_slots, free_slots):
    print("\n📌 Scheduling elective/supporting courses.")
    course_count = len(cou_list)
    assigned_course = 0
    # Separate tracking for reused slots
    used_continuous_slots = []
    used_free_slots = []

    for idx, c in enumerate(cou_list):
        print("\nNow for course ", c['course'], "and index ", idx)
        assigned_hours = 0
        cou = c['course']
        credits_hours = cou.credit_hours
        lab_hours = cou.lab_hours
        lecture_hours = cou.lecture_hours
        lab_room = c['lab']
        instructor = c['instructor']

        # Determine which slots to use (first course can use all, others must use used ones)
        available_continuous = continuous_slots if idx == 0 else used_continuous_slots
        available_free = free_slots if idx == 0 else used_free_slots

        if lab_room is not None:
            assigned_lab = 0
            assigned_lecture = 0

            # Temporary trackers for this course only
            course_used_continuous = []
            course_used_free = []

            # Assign lab (continuous first)
            while assigned_lab + 2 <= lab_hours:
                # Filter out slots already used by this course
                current_available_continuous = [slot for slot in available_continuous if slot not in course_used_continuous]

                cont_used, hours = assing_continuous_slots(cls, sem, cou, instructor, lab_room, current_available_continuous)
                if not cont_used or hours == 0:
                    break
                course_used_continuous.extend(cont_used)
                assigned_lab += hours
                assigned_hours += hours

            # Assign remaining lab with free slots
            while assigned_lab < lab_hours:
                current_available_free = [slot for slot in available_free if slot not in course_used_free]

                free_used, hours = assign_onebyone_slot(cls, sem, cou, instructor, lab_room, current_available_free)
                if not free_used or hours == 0:
                    break
                course_used_free.extend(free_used)
                assigned_lab += hours
                assigned_hours += hours

            if assigned_lab == lab_hours:
                print(f"✅ Successfully assigned all lab_hours for {cou.name}")
            else:
                print(f"⚠️ Could not assign full lab_hours for {cou.name}. Assigned: {assigned_lab}/{lab_hours}")

            # Now assign lecture (excluding lab-used slots)
            if lecture_hours:
                lab_room = None
                assigned_lecture = 0

                lecture_available_free = [
                    slot for slot in free_slots if slot not in course_used_free
                ]

                while assigned_lecture + 2 <= lecture_hours:
                    current_available_continuous = [slot for slot in available_continuous if slot not in course_used_continuous]

                    cont_used, hours = assing_continuous_slots(cls, sem, cou, instructor, lab_room, current_available_continuous)
                    if not cont_used or hours == 0:
                        break
                    course_used_continuous.extend(cont_used)
                    assigned_lecture += hours
                    assigned_hours += hours

                while assigned_lecture < lecture_hours:
                    current_available_free = [slot for slot in available_free if slot not in course_used_free]

                    free_used, hours = assign_onebyone_slot(cls, sem, cou, instructor, lab_room, current_available_free)
                    if not free_used or hours == 0:
                        break
                    course_used_free.extend(free_used)
                    assigned_lecture += hours
                    assigned_hours += hours

                if assigned_lecture == lecture_hours:
                    print(f"✅ Successfully assigned all lecture_hours for {cou.name}")
                else:
                    print(
                        f"⚠️ Could not assign full lecture_hours for {cou.name}. Assigned: {assigned_lecture}/{lecture_hours}")

            # After all done, add this course's used slots to global used lists
            used_continuous_slots.extend(course_used_continuous)
            used_free_slots.extend(course_used_free)

        else:
            lab_room = None
            assigned_credit = 0
            # Temporary trackers for this course only
            course_used_continuous = []
            course_used_free = []
            # Assign continuous pairs first
            while assigned_credit + 2 <= credits_hours:
                # Filter out slots already used by this course
                current_available_continuous = [slot for slot in available_continuous if slot not in course_used_continuous]

                cont_used, hours = assing_continuous_slots(cls, sem, cou, instructor, lab_room, current_available_continuous)
                if not cont_used or hours == 0:
                    break
                course_used_continuous.extend(cont_used)
                assigned_credit += hours
                assigned_hours += hours

            # Assign remaining hours with one-by-one slots

            while assigned_credit < credits_hours:
                current_available_free = [slot for slot in available_free if slot not in course_used_free]

                free_used, hours = assign_onebyone_slot(cls, sem, cou, instructor, lab_room, current_available_free)

                if not free_used or hours == 0:
                    break
                course_used_free.extend(free_used)
                assigned_credit += hours
                assigned_hours += hours

            # Final reporting
            if assigned_credit == credits_hours:
                print(f"✅ Successfully assigned all credit_hours for {cou.name}")
            else:
                print(f"⚠️ Could not assign full credit_hours for {cou.name}. Assigned: {assigned_credit}/{credits_hours}")

            # Add this course's used slots to global pool for future reuse
            used_continuous_slots.extend(course_used_continuous)

            used_free_slots.extend(course_used_free)

    if course_count == assigned_course:
        return True
    else:
        return False


def assing_continuous_slots(cls, sem, course, instructor, room, available_continuous):
    print("\nAvailable continuous:", available_continuous)
    if not available_continuous:
        return [], 0

    cont = None
    for option in available_continuous:
        day = option['day']
        # Check if there is any schedule on this day
        has_schedule = Timetable_Schedule.objects.filter(
            classroom = cls,
            course=course,
            day=day
        ).exists()

        if not has_schedule:
            cont = option
            break

    # Fallback: if all options have schedules, use the first one anyway
    if cont is None:
        return [], 0

    # Extract day and slots
    day = cont['day']
    slots = cont['slots'] # list of 2 times

    for slot in slots:
        save_schedule_entry(sem, course, instructor, cls, room, day, slot)

    print("Cont;", cont)

    return [cont], 2


def assign_onebyone_slot(cls, sem, course, instructor, room, available_free):
    print("\nAvailable free:", available_free)

    for slot_info in available_free:

        day = slot_info['day']

        has_schedule = Timetable_Schedule.objects.filter(
            classroom = cls,
            course=course,
            day=day
        ).exists()

        if has_schedule:
            continue

        slot = slot_info['slot']

        save_schedule_entry(sem, course, instructor, cls, room, day, slot)
        print("Slot_info", slot_info)

        return [slot_info], 1
    return [], 0


def save_schedule_entry(sem, course, instructor, cls, room, day, time_slot):
    print("\nSaving entry.")
    # Save this entry to your database
    Timetable_Schedule.objects.create(
        semester=sem,
        classroom=cls,
        course= course,
        lab_room=room,
        instructor=instructor,
        start_time=time_slot,
        day=day
    )
    print("Successfully saved.\n")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def timetable_list(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    rooms = Timetable_Schedule.objects.filter(semester=semester).values_list('classroom', flat=True).distinct()
    classrooms = Classroom.objects.filter(id__in=rooms)

    print(semester)
    return render(request, 'timetable_list.html', {
        'classrooms': classrooms,
        'semester': semester,
        'semester_id': semester_id
    })


def each_classroom_timetable(request, classroom_id, semester_id):
    print("\nStarting each_classroom_timetable")
    print("\nClassroom id: ", classroom_id)

    semester = Semester.objects.get(id=semester_id)
    print("\nSemester:", semester)

    classrooms = []
    course_instructor_list = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slot = ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "Break Time", "1:00 - 2:00", "2:00 - 3:00", "3:00 - 4:00"]
    start_times = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]

    # Fetch classroom and its related major names
    classroom = Classroom.objects.get(id=classroom_id)
    room_info = {
        'classroom': {
            'id': classroom.id,
            'room_number': classroom.room_number,
            'majors': [major.name for major in classroom.majors.all()]
        },
        'schedule': []
    }
    print("\nRoom info:", room_info)

    # Get course-instructor mapping for this classroom
    course_instructor = Timetable_Schedule.objects.filter(classroom=room_info['classroom']['id']) \
        .values('course', 'instructor')

    unique_courses = set()
    for ci in course_instructor:
        course_name = Course.objects.filter(id=ci['course']).values_list('name', flat=True).first() or ''
        instructor_name = User.objects.filter(id=ci['instructor']).values_list('first_name', flat=True).first() or ''

        course_tuple = (course_name, instructor_name)
        if course_tuple not in unique_courses:
            unique_courses.add(course_tuple)
            course_instructor_list.append({
                'course_name': course_name,
                'instructor_name': instructor_name,
                'classroom': room_info['classroom']
            })

    # Build schedule day by day
    for day in days:
        day_course = {'day': day, 'courses': []}
        courses = Timetable_Schedule.objects.filter(
            classroom=classroom_id,
            semester=semester,
            day=day
        ).values('course', 'instructor', 'start_time', 'lab_room').order_by('start_time')

        for time in start_times:
            time_obj = datetime.strptime(time, "%H:%M").time()
            slot_courses = []

            for course_data in courses:
                if time_obj == course_data['start_time']:
                    # Add labroom name if labroom is not None
                    lab_name = ''
                    if course_data.get('lab_room'):
                        lab = Classroom.objects.filter(id=course_data['lab_room']).first()
                        if lab:
                            lab_name = lab.room_number

                    course_entry = {
                        'course_name': Course.objects.filter(id=course_data['course']).values_list('name', flat=True).first() or '',
                        'instructor': User.objects.filter(id=course_data['instructor']).values_list('first_name', flat=True).first() or '',
                        'start_time': str(course_data['start_time']),
                        'lab_name': lab_name,  # ✅ Add lab name to display
                    }
                    slot_courses.append(course_entry)

            # Handle multiple courses at same slot
            if len(slot_courses) > 1:
                course_names = '/'.join([
                    f"{course['course_name']} ({course['lab_name']})" if course.get('lab_name')
                    else course['course_name']
                    for course in slot_courses
                ])
                course_entry = {
                    'course_name': course_names,
                    'instructor': '',
                    'start_time': str(time),
                    'lab_name': '',  # Skip lab name if mixed
                }
            elif slot_courses:
                course_entry = slot_courses[0]
            else:
                course_entry = {
                    'course_name': ' ',
                    'instructor': '',
                    'start_time': str(time),
                    'lab_name': '',
                }

            day_course['courses'].append(course_entry)

        room_info['schedule'].append(day_course)

    classrooms.append(room_info)

    return render(request, 'timetable.html', {
        'classrooms': classrooms,
        'start_times': slot,
        'instructors': course_instructor_list,
        'semester_id': semester_id

    })

@login_required
@user_passes_test(lambda u: is_in_group(u, "Instructor"))
def teacher_timetable(request, instructor_id):
    instructor_instance = User.objects.get(id=instructor_id)
    first_name = User.objects.get(id=instructor_id).first_name
    information = Timetable_Schedule.objects.filter(instructor=instructor_instance).values('classroom', 'day', 'start_time', 'course')
    print("\nInstructor_instance: ", instructor_instance)
    print("\nInformation: ", information)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "Break Time", "1:00 - 2:00", "2:00 - 3:00",
             "3:00 - 4:00"]
    start_times = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]

    schedule = []

    for day in days:
        day_set = {
            'day': day,
            'room': []
        }
        rooms = (Timetable_Schedule.objects.filter(
            day=day, instructor=instructor_id).values(
            'classroom', 'course','start_time','lab_room')
            .order_by('start_time'))
        print("\nRooms:", rooms)

        for time in start_times:
            time_obj = datetime.strptime(time, "%H:%M").time()
            room_entry = None
            for room in rooms:
                print("\nRoom: ", room)
                if time_obj == room['start_time']:  # Check if course exists for this time slot
                    if room['lab_room'] == None:
                        room_entry = {
                            'room_number': Classroom.objects.get(id=room['classroom']).room_number,
                            'course': Course.objects.filter(id=room['course']).values_list('course_id', flat=True).first() or '',
                            'semester': 'semester:' + str(Classroom.objects.filter(id=room['classroom']).values_list('semesters', flat=True).first() or ''),
                            'start_time': str(room['start_time']),  # Convert to string for consistency
                        }
                        break  # Stop looping once we find a matching course
                    else:
                        room_entry = {
                            'room_number': Classroom.objects.get(id=room['lab_room']).room_number,
                            'course': Course.objects.filter(id=room['course']).values_list('course_id',flat=True).first() or '',
                            'semester': 'semester:' + str(Classroom.objects.filter(id=room['classroom']).values_list('semesters',flat=True).first() or ''),
                            'start_time': str(room['start_time']),  # Convert to string for consistency
                        }
                        break  # Stop looping once we find a matching course
            if not room_entry:
                room_entry = {
                    'room_number': '',
                    'course': '',
                    'semester': "",
                    'start_time': str(time),
                }
            print("Room:", room_entry)
            day_set['room'].append(room_entry)
        schedule.append(day_set)
        print("\nSchedule:", schedule)
    return render(request, "instructor_view.html", {'schedule': schedule, 'slots': slots, 'first_name': first_name})


def each_classroom_timetable_delete(request, semester_id, classroom_id):
    print("Deleting all schedule of room", classroom_id, "of semester", semester_id)

    classroom = Classroom.objects.get(id=classroom_id)
    semester = Semester.objects.get(id=semester_id)

    Match_instructorANDcourse.objects.filter(classroom=classroom, semester=semester).delete()
    LabroomUsed.objects.filter(room=classroom, semester=semester).delete()
    Timetable_Schedule.objects.filter(classroom=classroom, semester=semester).delete()

    print("✅ Deletion completed.")
    return redirect(reverse('timetable_list', args=[semester_id]))

def lab_room_timetable_list(request):
    print("This is labroom Timetable display page.",)
    labs = Classroom.objects.filter(is_lab=True)
    print("All lab:",labs)

    return render(request, 'labroom_list.html', {'labs':labs})

def labroom_timetable(request, lab_id):
    print("Lab id:", lab_id)
    lab = Classroom.objects.get(id=lab_id)

    print("lab",lab)

    scheduled_lab = Timetable_Schedule.objects.filter(lab_room=lab)
    print("Schedule", scheduled_lab)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "Break Time", "1:00 - 2:00", "2:00 - 3:00",
             "3:00 - 4:00"]
    start_times = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]

    schedule = []

    for day in days:
        day_set = {
            'day': day,
            'room': []
        }
        rooms = (Timetable_Schedule.objects.filter(day=day, lab_room=lab).
                 values('classroom', 'course', 'start_time', 'lab_room').
                 order_by ('start_time'))
        print("\nRooms:", rooms)

        for time in start_times:
            time_obj = datetime.strptime(time, "%H:%M").time()
            room_entry = None
            for room in rooms:
                print("\nRoom: ", room)
                if time_obj == room['start_time']:  # Check if course exists for this time slot
                    room_entry = {
                        'room_number': Classroom.objects.get(id=room['classroom']).room_number,
                        'course': Course.objects.filter(id=room['course']).values_list('course_id', flat=True).first() or '',
                        'semester': 'semester:' + str(Classroom.objects.filter(id=room['classroom']).values_list('semesters', flat=True).first() or ''),
                        'start_time': str(room['start_time']),  # Convert to string for consistency
                    }
                    break  # Stop looping once we find a matching course
            if not room_entry:
                room_entry = {
                    'room_number': '',
                    'course': '',
                    'semester': "",
                    'start_time': str(time),
                }
            print("Room:", room_entry)
            day_set['room'].append(room_entry)
        schedule.append(day_set)
        print("\nSchedule:", schedule)
    return render(request, "labroom_timetable.html", {'schedule': schedule, 'slots': slots, 'lab_name': lab.room_number})

#Part for merge timetables
def get_classrooms_by_semester(request, semester_id):
    print("\nGet classroom by semester.")
    classrooms = Classroom.objects.filter(
        main_class__semester_id=semester_id
    ).distinct()
    data = []
    for c in classrooms:
        print(c.room_number)
        room={
            'id': c.id,
            'name': c.room_number
        }
        data.append(room)
    return JsonResponse(data, safe=False)

def get_courses_by_classroom(request, classroom_id):
    print("\nGet courses by classroom.")
    classroom = Classroom.objects.get(id=classroom_id)
    courses = Course.objects.filter(
        timetable_schedule__classroom=classroom
    ).distinct()

    print("Selected courses")
    for c in courses:
        print(c.course_id)

    data = [{'id': c.id, 'course_id': c.course_id} for c in courses]
    return JsonResponse(data, safe=False)

@login_required()
def display_semester(request):
    print("\nDisplay semester to choose for merging timetables.")

    scheduled_semesters = Semester.objects.filter(timetable_schedule__isnull=False).distinct()

    semesters = []
    print("Scheduled semesters:")
    for s in scheduled_semesters:
        print(s.name)
        semesters.append(s)

    if request.method == "POST":
        print("\nPost request sent from merge_one page.")

        semester_id = request.POST.get('semester')
        classroom_id = request.POST.get('classroom')
        course_id = request.POST.get('course')

        head_merge={
            'semester': semester_id,
            'classroom': classroom_id,
            'course': course_id
        }

        print("Received POST data:")
        print("Semester ID:", semester_id)
        print("Classroom ID:", classroom_id)
        print("Course ID:", course_id)

        request.session["head_merge"] = head_merge
        return redirect("go_to_mergeTwo")

    return  render(request, "merged_one.html", {'semesters': semesters})

def take_slots_of_head_merge(head):
    print("\nTake slots of head merge:")

    cls = Classroom.objects.get(id=head['classroom_id'])
    sem = Semester.objects.get(id=head['sem_id'])
    course = Course.objects.get(id=head['course_id'])

    lab_slots = []
    lecture_slots = []

    lab_id = head['lab_id']
    print("Lab_id:",lab_id)
    if lab_id:
        lab = Classroom.objects.get(id=lab_id)

        lab_slots = list(
            Timetable_Schedule.objects.filter(
                classroom=cls,
                semester=sem,
                course=course,
                lab_room=lab
            ).values('day', 'start_time')
        )

    else:
        lab_slots = []

    lecture_slots = list(Timetable_Schedule.objects.filter(
        classroom=cls,
        semester=sem,
        course=course,
        lab_room=None
    ).values('day', 'start_time'))

    slots = {
        'lecture_slots': lecture_slots,
        'lab_slots': lab_slots
    }

    print('\n--- Slots Taken by Head Classroom ---')
    for key, value in slots.items():
        print(f"{key}: {value}")

    return slots

def get_mergeable_classrooms(request):
    global head
    print("\nGet mergeable classrooms")
    head_merge = request.session.get("head_merge")

    semester = Semester.objects.get(id=head_merge['semester'])

    classroom_id = head_merge['classroom']
    print("classroom_id:", classroom_id)
    cls = Classroom.objects.get(id=classroom_id)

    course = Course.objects.get(id=head_merge['course'])
    print("Course:",course)
    flag = course.lab_required
    print("Flag:",flag)

    if flag == True:
        labElement = LabroomUsed.objects.get(room=cls, course=course, semester=semester)
        lab_name = labElement.lab_room
        lab = Classroom.objects.get(room_number = lab_name)
    else:
        lab = None

    match = Match_instructorANDcourse.objects.get(course=course, classroom= cls)
    instructor_id = match.instructor.id
    instructor_first_name = match.instructor.first_name

    classrooms = Classroom.objects.filter(
        main_class__course=course
    ).distinct()

    grouped = []

    for c in classrooms:
        if c.id == int(classroom_id):
            continue

        sem = c.semesters.name
        classroom_data = {"id": c.id, "name": c.room_number}

        # Check if sem already exists in grouped
        found = False
        for group in grouped:
            if group["sem"] == sem:
                group["classrooms"].append(classroom_data)
                found = True
                break

        if not found:
            grouped.append({
                "sem": sem,
                "classrooms": [classroom_data]
            })

        head = {
            'classroom_id' : classroom_id,
            'sem_id' : head_merge['semester'],
            'course_id': head_merge['course'],
            'instructor': instructor_id,
            'lab_id' : ''
        }

        if flag == True:
            head['lab_id'] = lab.id

    if request.method == "POST":
        print("\nPost request was sent from mergerd_two page.")

        wanna_merge = []

        selected_classroom_ids = request.POST.get("selected_classrooms", "")
        selected_classroom_ids = [int(id.strip()) for id in selected_classroom_ids.split(",") if id.strip().isdigit()]
        print("Selected ids:", selected_classroom_ids)

        for r in selected_classroom_ids:
            wanna_merge.append(r)

        selected_instructors_ids = request.POST.get("selected_instructors", "")
        selected_instructors_ids = [int(id.strip()) for id in selected_instructors_ids.split(",")if id.strip().isdigit()]
        print("Selected instructors:", selected_instructors_ids)

        selected_lab_id = 0
        if flag == True:
            selected_lab_id = request.POST.get("lab")
            print("Selected labs:", selected_lab_id)

        main_objects = {
            'instructors_ids': selected_instructors_ids,
            'selected_lab_id': selected_lab_id
        }

        main_slots = take_slots_of_head_merge(head)

        if main_slots:
            OK = merging(head, main_slots, wanna_merge, main_objects)
            if OK:
                request.session['head_classroom'] = classroom_id
                request.session['wanna_merge'] = wanna_merge
                request.session['main_objects'] = main_objects
                request.session['course'] = course.id
                return redirect("/merged_list")

    return render (request, "merged_two.html", {'data':grouped, 'sem':semester.name, 'room': cls, 'instructor':instructor_first_name, 'instructor_id':instructor_id, 'subject':course, 'flag':flag, 'lab':lab})

def take_schedules(classroom, semester, course):
    print("\nTake schedules")
    WEEKDAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if course:
        schedules = list(Timetable_Schedule.objects.filter(
            classroom=classroom,
            semester=semester,
            course=course
        ))

    else:
        schedules = list(Timetable_Schedule.objects.filter(
            classroom=classroom,
            semester=semester,
        ))

    schedules.sort(key=lambda x: (WEEKDAY_ORDER.index(x.day), x.start_time))

    return schedules

def take_related_schedules(classroom, semester, selected_schedule):
    print("\nTake related schedules")
    WEEKDAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    schedules = []
    for s in selected_schedule:
        related_sch = Timetable_Schedule.objects.filter(
            classroom=classroom,
            semester=semester,
            day=s.day,
            start_time=s.start_time
        ).exclude(id=s.id)  # Exclude the same schedule by ID

        schedules.extend(list(related_sch))  # Flatten into the main list

    # Sort schedules by weekday and time
    schedules.sort(key=lambda x: (WEEKDAY_ORDER.index(x.day), x.start_time))

    return schedules

def reschedule(schedule, room, semester):
    print("\nReschedule")
    flag = Timetable_Schedule.objects.create(
        classroom = room,
        semester = semester,
        course = schedule.course,
        instructor = schedule.instructor,
        lab_room = schedule.lab_room,
        day = schedule.day,
        start_time = schedule.start_time
    )

    if flag:
        return True

    return False


def delete_old_schedules(room, semester, course):
    print("\nDelete one old slots")
    print("Course:",course)

    flag = Timetable_Schedule.objects.filter(
        classroom = room,
        semester = semester,
        course = course
    ).delete()
    print("Flag:", flag ,"\n")
    return flag

def find_free_and_assign(schedule, except_schedules):
    print("Assign to free schedule")

    # Normalize to list
    if not isinstance(schedule, (list, tuple)):
        schedule = [schedule]

    if not schedule:
        print("Empty schedule list.")
        return False

    slots = [time(hour) for hour in range(9, 12)] + [time(hour) for hour in range(13, 15)]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # Convert except_schedules to a set of (day, time) tuples for fast lookup
    except_set = set(except_schedules)

    try:
        with transaction.atomic():
            for day in days:
                for slot in slots:
                    if (day, slot) in except_set:
                        print(f"Skipping {day} at {slot} due to exception.")
                        continue

                    print(f"Checking {day} at {slot}")
                    conflict_found = False

                    for sch in schedule:
                        # Check if the classroom slot is free
                        class_conflict = Timetable_Schedule.objects.filter(
                            classroom=sch.classroom,
                            day=day,
                            start_time=slot
                        ).exists()

                        # Check instructor conflict
                        instructor_conflict = Timetable_Schedule.objects.filter(
                            instructor=sch.instructor,
                            day=day,
                            start_time=slot
                        ).exists()

                        # Check lab conflict if needed
                        lab_conflict = False
                        if sch.lab_room:
                            lab_conflict = Timetable_Schedule.objects.filter(
                                lab_room=sch.lab_room,
                                day=day,
                                start_time=slot
                            ).exists()

                        if class_conflict or instructor_conflict or lab_conflict:
                            print(f"Conflict for {sch.course} at {day} {slot}")
                            conflict_found = True
                            break

                    if not conflict_found:
                        # No conflicts for any schedule object: assign all
                        for sch in schedule:
                            sch.day = day
                            sch.start_time = slot
                            sch.save()
                            print(f"Assigned {sch.course} to {day} at {slot}")
                        return True

            print("No common free slot found for all schedules.")
            return False

    except Exception as e:
        print("Assignment failed:", e)
        return False


def update_schedule(schedule, day, start_time):
    print("\nUpdate Schedule:", schedule)
    schedule.day = day
    schedule.start_time = start_time
    schedule.save()
    return True
@transaction.atomic()
def merging(head, main_slots, wanna_merge, main_objects):
    print("\nStart merging.")

    #Collecting merge head detail and main instructor and course
    head_classroom = Classroom.objects.get(id=head['classroom_id'])
    head_semester = Semester.objects.get(id=head['sem_id'])
    instructor = User.objects.get(id=head['instructor'])
    course = Course.objects.get(id=head['course_id'])
    lab = None
    if head['lab_id']:
        lab = Classroom.objects.get(id=head['lab_id'])

    main_schedules = take_schedules(head_classroom, head_semester, course)

    print("\n--------")
    try:
        with transaction.atomic():
            i = 0
            for r in wanna_merge:
                room = Classroom.objects.get(id=r)
                print("Current classroom:", room.room_number)
                semester = room.semesters
                print("Semester of current classroom is ", semester)

                flag1 = Match_instructorANDcourse.objects.filter(
                    classroom=room,
                    semester=semester,
                    course=course
                ).update(instructor=instructor)

                if lab:
                    flag2 = LabroomUsed.objects.filter(
                        room=room,
                        semester=semester,
                        course=course
                    ).update(lab_room=lab.room_number)

                old_schedules= take_schedules(room, semester, course)
                same_slots_schedules = take_related_schedules(room, semester , old_schedules)

                delete = delete_old_schedules(room, semester, course)


                target_schedules = take_schedules(room, semester, None)
                target_schedule_slots = set((s.day, s.start_time) for s in target_schedules)

                if same_slots_schedules:
                    schedule_pairs = itertools.zip_longest(main_schedules, same_slots_schedules)
                else:
                    schedule_pairs = [(ms, None) for ms in main_schedules]

                for main_schedule, related_schedule in schedule_pairs:
                    print("Current schedule to assign is ", main_schedule)
                    key = (main_schedule.day, main_schedule.start_time)
                    if key in target_schedule_slots:
                        current_target_schedule = [
                            s for s in target_schedules
                            if s.day == main_schedule.day and s.start_time == main_schedule.start_time
                        ]
                        print("There is target schedule in the same day and time:", current_target_schedule)

                        flag3 = find_free_and_assign(current_target_schedule, main_schedules)
                        if flag3:
                            flag4 = reschedule(main_schedule, room, semester)
                            if flag4:
                                if related_schedule:
                                    flag5 = update_schedule(related_schedule, main_schedule.day, main_schedule.start_time)
                                    if flag5:
                                        print("Successfully update related course's schedule:")
                                print("Successfully assigned main schedule and successfully swapped the current target schedule")
                    else:
                        print("Can Schedule freely")
                        flag3 = reschedule(main_schedule, room, semester)
                        if flag3:
                            if related_schedule:
                                flag5 = update_schedule(related_schedule, main_schedule.day, main_schedule.start_time)
                                if flag5:
                                    print("Successfully update related course's schedule:")
                        print("Successfully reschedule.")

    except Exception as e:
        print("Merging failed:", e)
        return False

    return True

def display_merged_list(request):
    print("\nTaking Merged classroom list.")
    head_classroom = request.session.get('head_classroom')
    room_ids = request.session.get('wanna_merge')

    sub_id = request.session.get('course')

    subject = Course.objects.get(id=sub_id)
    print("Subject", subject)


    h_room = Classroom.objects.get(id=head_classroom)
    h_semester = h_room.semesters
    print("H semester id",h_semester.id)
    print("Head classroom:",h_room)

    semester = Semester.objects.get(name=h_semester)

    rooms = Classroom.objects.filter(id__in=room_ids)
    print("Merged classroom IDs:", rooms)

    for r in rooms:
        print("Semester id :", r.semesters.id)
    return render(request, "merged_list.html", {'head':h_room, 'subject': subject, 'rooms': rooms, 'semester': h_semester})

def swap_timetable(request, classroom_id, semester_id):

        print("\nClassroom id: ", classroom_id)

        semester = Semester.objects.get(id=semester_id)

        classrooms = []
        course_instructor_list = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        slot = ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "Break Time", "1:00 - 2:00", "2:00 - 3:00",
                "3:00 - 4:00"]
        start_times = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]

        # Fetch classroom and its related major names
        classroom = Classroom.objects.get(id=classroom_id)
        room_info = {
            'classroom': {
                'id': classroom.id,
                'room_number': classroom.room_number,
                'majors': [major.name for major in classroom.majors.all()]
            },
            'schedule': []
        }

        # Get course-instructor mapping for this classroom
        course_instructor = Timetable_Schedule.objects.filter(classroom=room_info['classroom']['id']) \
            .values('course', 'instructor')

        unique_courses = set()
        for ci in course_instructor:
            course_name = Course.objects.filter(id=ci['course']).values_list('name', flat=True).first() or ''
            instructor_name = User.objects.filter(id=ci['instructor']).values_list('first_name',
                                                                                   flat=True).first() or ''

            course_tuple = (course_name, instructor_name)
            if course_tuple not in unique_courses:
                unique_courses.add(course_tuple)
                course_instructor_list.append({
                    'course_name': course_name,
                    'instructor_name': instructor_name,
                    'classroom': room_info['classroom']
                })

        # Build schedule day by day
        for day in days:
            day_course = {'day': day, 'courses': []}
            courses = Timetable_Schedule.objects.filter(
                classroom=classroom_id,
                semester=semester,
                day=day
            ).values('course', 'instructor', 'start_time', 'lab_room').order_by('start_time')

            for time in start_times:
                time_obj = datetime.strptime(time, "%H:%M").time()
                slot_courses = []

                for course_data in courses:
                    if time_obj == course_data['start_time']:
                        # Add labroom name if labroom is not None
                        lab_name = ''
                        if course_data.get('lab_room'):
                            lab = Classroom.objects.filter(id=course_data['lab_room']).first()
                            if lab:
                                lab_name = lab.room_number

                        course_entry = {
                            'id': [Course.objects.filter(id=course_data['course']).values_list('id',
                                                                                               flat=True).first()] or '',
                            'course_name': Course.objects.filter(id=course_data['course']).values_list('name',
                                                                                                       flat=True).first() or '',
                            'instructor': User.objects.filter(id=course_data['instructor']).values_list('first_name',
                                                                                                        flat=True).first() or '',
                            'start_time': str(course_data['start_time']),
                            'lab_name': lab_name,  # ✅ Add lab name to display

                        }

                        slot_courses.append(course_entry)

                # Handle multiple courses at same slot

                if len(slot_courses) > 1:
                    course_ids = [cid for course in slot_courses for cid in course['id']]
                    print(course_ids)
                    course_names = '/'.join([
                        f"{course['course_name']} ({course['lab_name']})" if course.get('lab_name')
                        else course['course_name']
                        for course in slot_courses
                    ])
                    course_entry = {
                        'id': course_ids,
                        'course_name': course_names,
                        'instructor': '',
                        'start_time': str(time),
                        'lab_name': '',  # Skip lab name if mixed
                    }
                elif slot_courses:
                    course_entry = slot_courses[0]
                else:
                    course_entry = {
                        'id': '',
                        'course_name': ' ',
                        'instructor': '',
                        'instructor_id': '',
                        'start_time': str(time),
                        'lab_name': '',
                    }

                    course_entry['is_free'] = (
                            course_entry['course_name'].strip() == '' and str(course_entry['start_time']) not in [
                        '12:00:00'])

                day_course['courses'].append(course_entry)

            room_info['schedule'].append(day_course)

        classrooms.append(room_info)
        request.session['course_entry'] = classrooms
        request.session['semester_id'] = semester_id
        return render(request, 'swap_timetable.html', {
            'classrooms': classrooms,
            'start_times': slot,
            'instructors': course_instructor_list,
            'semester_id': semester_id,
            'classroom_id': classroom_id
        })


@login_required
def swap_options(request):


    swappable_slots = []

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    course_ids_raw = request.GET.get('course_ids')
    course_ids = json.loads(course_ids_raw) if course_ids_raw else []

    classroom_id = request.GET.get('classroom_id')
    selected_day = request.GET.get('day')
    selected_time = request.GET.get('time')

    selected_classroom = Classroom.objects.get(id=classroom_id)

    # SELECTED SLOTS
    selected_slots = Timetable_Schedule.objects.filter(
        course__id__in=course_ids,
        day=selected_day,
        start_time=selected_time,
        classroom__id=classroom_id
    )

    # OTHER SLOTS (excluding selected ones)
    same_classroom_slots = Timetable_Schedule.objects.filter(
        classroom=selected_classroom
    ).exclude(
        id__in=[s.id for s in selected_slots]
    )

    # Group target slots by (day, start_time)
    target_slot_groups = defaultdict(list)
    for slot in same_classroom_slots:
        key = (slot.day, slot.start_time)
        target_slot_groups[key].append(slot)

    semester = request.session.get('semester_id', '')

    for (target_day, target_time), target_group in target_slot_groups.items():
        # STEP 1: Check if all selected can move to target time
        can_move_all = True
        for selected in selected_slots:
            instructor_busy = Timetable_Schedule.objects.filter(
                instructor=selected.instructor,
                day=target_day,
                start_time=target_time
            ).exists()
            lab_busy = selected.lab_room and Timetable_Schedule.objects.filter(
                lab_room=selected.lab_room,
                day=target_day,
                start_time=target_time
            ).exists()
            if instructor_busy or lab_busy:
                can_move_all = False
                break

        if not can_move_all:
            continue

        # STEP 2: Check if all target group can move to selected time
        can_swap_all = True
        for target in target_group:
            instructor_busy = Timetable_Schedule.objects.filter(
                instructor=target.instructor,
                day=selected_day,
                start_time=selected_time
            ).exists()
            lab_busy = target.lab_room and Timetable_Schedule.objects.filter(
                lab_room=target.lab_room,
                day=selected_day,
                start_time=selected_time
            ).exists()
            if instructor_busy or lab_busy:
                can_swap_all = False
                break

        if can_swap_all:
            # Get course type for formatting time
            course = target_group[0].course  # assume same course type in group
            course_type = CourseSemesterInfo.objects.filter(
                course=course,
                semester__id=semester
            ).values_list('type', flat=True).first()

            swappable_slots.append({
                'day': target_day,
                'time': str(target_time),
                'classroom_id': classroom_id
            })

    print("Swappable slots found:")
    for s in swappable_slots:
        print(s)


    session_data = request.session.get('course_entry', {})
    additional_swappables = []

    free_slots = {}

    for session in session_data:
        for schedule in session.get("schedule", []):
            day = schedule["day"]
            free_times = [c["start_time"] for c in schedule["courses"] if
                          c.get("is_free") and c["start_time"] != "12:00"]
            free_slots[day] = free_times

    for day in days:
        for time in free_slots.get(day, []):
            conflict_found = False
            for selected_slot in selected_slots:

                class_conflict = Timetable_Schedule.objects.filter(
                    classroom=selected_slot.classroom,
                    day=day,
                    start_time=time
                ).exists()

                # Check instructor conflict
                instructor_conflict = Timetable_Schedule.objects.filter(
                    instructor=selected_slot.instructor,
                    day=day,
                    start_time=time
                ).exists()

                # Check lab conflict if needed
                lab_conflict = False
                if selected_slot.lab_room:
                    lab_conflict = Timetable_Schedule.objects.filter(
                        lab_room=selected_slot.lab_room,
                        day=day,
                        start_time=time
                    ).exists()

                if class_conflict or instructor_conflict or lab_conflict:
                    print(f"Conflict for {selected_slot.course} at {day} {time}")
                    conflict_found = True
                    break

            if not conflict_found:
                additional_swappables.append({
                    'day': day,
                    'time': str(time),
                    'classroom_id': classroom_id,
                    'is_free_slot': True,

                })

    swappable_slots.extend(additional_swappables)
    print("Final Swappable")
    for s in swappable_slots:
        print(s)
    seen = set()
    unique_slots = []

    for slot in swappable_slots:
        key = (slot['day'], slot['time'])
        if key not in seen:
            seen.add(key)
            unique_slots.append(slot)


    return JsonResponse({'swappable_slots': unique_slots})


def safe_parse_time(time_str):
    if not time_str:
        return None
    if time_str.count(':') == 1:  # HH:MM format
        return parse_time(time_str + ':00')
    return parse_time(time_str)  # HH:MM:SS format


@csrf_exempt
def confirm_swap(request):
    try:
        data = json.loads(request.body)

        first_selected_data = data['course1']
        second_selected_data = data['course2']
        first_course_ids_raw = first_selected_data['course_id']
        first_course_ids = ast.literal_eval(first_course_ids_raw)

        first_selected_courses = Timetable_Schedule.objects.filter(
            course__id__in=first_course_ids,
            day=first_selected_data['day'],
            start_time=safe_parse_time(first_selected_data['time']),
            classroom__id=first_selected_data['classroom_id']
        )
        print("FirstCourse", first_selected_courses)

        first_day = first_selected_data['day']
        first_time = safe_parse_time(first_selected_data['time'])

        second_day = second_selected_data['day']
        second_time = safe_parse_time(second_selected_data['time'])

        if second_selected_data['course_id'] != '':
            second_course_ids_raw = second_selected_data['course_id']
            second_course_ids = ast.literal_eval(second_course_ids_raw)

            second_selected_courses = Timetable_Schedule.objects.filter(
                course__id__in=second_course_ids,
                day=second_selected_data['day'],
                start_time=safe_parse_time(second_selected_data['time']),
                classroom__id=second_selected_data['classroom_id']
            )

            print("SecondCourse", second_selected_courses)

            for course in first_selected_courses:
                course.day = second_day
                course.start_time = second_time
                course.save()

            for course in second_selected_courses:
                course.day = first_day
                course.start_time = first_time
                course.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Course moved successfully'
            })

        else:
            print("SecondCourse_id", second_selected_data['course_id'])
            print("SecondCourse_id")

            for course in first_selected_courses:
                course.day = second_day
                course.start_time = second_time
                course.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Course moved successfully'
            })

    except Timetable_Schedule.DoesNotExist as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Course not found: {str(e)}'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Swap failed: {str(e)}'
        }, status=500)
