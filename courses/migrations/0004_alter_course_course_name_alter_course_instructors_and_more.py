# Generated by Django 5.2.4 on 2025-07-04 06:47

import django_jalali.db.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_alter_course_options_alter_coursesession_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='instructors',
            field=models.ManyToManyField(blank=True, related_name='instructed_courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='course',
            name='start_date',
            field=django_jalali.db.models.jDateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
