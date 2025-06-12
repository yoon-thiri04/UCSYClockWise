from django.contrib import admin
from .models import Department,Major,Course,CourseSemesterInfo,Classroom,Semester,User,UserProfile,Timetable_Schedule,Match_instructorANDcourse,Company,CompanyGroup,Feedback,Subscriber,LabroomUsed
from django.contrib.auth.admin import UserAdmin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

admin.site.register(Department)
admin.site.register(CourseSemesterInfo)
admin.site.register(Timetable_Schedule)
admin.site.register(Major)
admin.site.register(Course)
admin.site.register(Classroom)
admin.site.register(Semester)
admin.site.register(Company)
admin.site.register(CompanyGroup)
admin.site.unregister(User)
admin.site.register(Feedback)
admin.site.register(Subscriber)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Match_instructorANDcourse)
admin.site.register(LabroomUsed)