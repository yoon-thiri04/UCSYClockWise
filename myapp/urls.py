from django.urls import path
from django.contrib.auth.views import PasswordChangeDoneView

from . import views
urlpatterns =[
    path('admin_home/',views.admin_home,name='admin-home'),
    path('choose_semester/', views.choose_semester, name='choose-semester'),
    path('viewPage/',views.viewPage,name='view-Page'),
    path('generate/',views.select_semester,name='generate'),
    path('view/',views.view_admin,name='view'),
    path('semester_ten/',views.semester_ten,name='semester-ten'),
    path('timetable_list/<int:semester_id>/',views.timetable_list,name='timetable_list'),
    path('classroom_timetable/<int:semester_id>/<int:classroom_id>/',views.each_classroom_timetable,name='classroom-timetable'),
    path('classroom_delete/<int:semester_id>/<int:classroom_id>/',views.each_classroom_timetable_delete,name='classroom-delete'),
    path('fill_room_data/<int:semester_id>',views.fill_rooms,name='fill_room_data'),
    path('assign_groups/',views.assign_groups,name='assign-groups'),
    #path('view_assign_groups',views.view_assign_groups,name='view-assign-groups'),
    path("assign_instructors/", views.assign_instructors, name="assign_instructors"),
    path("get_instructors/", views.get_instructors, name="get_instructors"),
    path('show_list/',views.showlist),
    path('login/',views.loginForm,name='login'),
    path('logout/',views.logOut,name='log-out'),
    path('account/',views.user_account, name='user-account'),
    #path('Generate_schedule/',views.schedule_generating,name="Generate_schedule"),
    path('timetable/<int:semester_id>/', views.classroom_timetable, name='classroom_timetable'),
    path('teacherTest/',views.teacherTest),
    path('teacher_view/<int:instructor_id>/',views.teacher_timetable,name='teacher_view'),
    path('lab_room_timetable_list',views.lab_room_timetable_list,name='lab_room_timetable_list'),
    path('labroom_timetable/<int:lab_id>',views.labroom_timetable,name='labroom-timetable'),
    path('merged_timetable', views.display_semester, name='merged-timetable'),
    path('get-classrooms/<int:semester_id>/', views.get_classrooms_by_semester, name='get_classrooms'),
    path('get-courses/<int:classroom_id>/', views.get_courses_by_classroom, name='get_courses'),
    path('go_to_mergeTwo/', views.get_mergeable_classrooms, name='go_to_mergeTwo'),
    path('merged_list/', views.display_merged_list, name='merged-list'),
    path('swap_timetable/<int:classroom_id>/<int:semester_id>/',views.swap_timetable,name='swap_timetable'),
    path('swap-options/', views.swap_options, name='swap-options'),
    path('confirm-swap/', views.confirm_swap, name='confirm_swap'),


]
