# Generated by Django 5.1.4 on 2025-05-23 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_remove_course_type_coursesemesterinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='type',
            field=models.CharField(choices=[('elective', 'elective'), ('supporting', 'supporting'), ('general', 'general'), ('major', 'major')], default='general', max_length=15),
        ),
        migrations.DeleteModel(
            name='CourseSemesterInfo',
        ),
    ]
