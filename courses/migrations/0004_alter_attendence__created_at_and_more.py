# Generated by Django 5.2.1 on 2025-06-04 17:49

import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_alter_course_course_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendence',
            name='_created_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='attendence',
            name='_updated_at',
            field=django_jalali.db.models.jDateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='attendence',
            name='attended_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='_created_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='_updated_at',
            field=django_jalali.db.models.jDateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='_created_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='_updated_at',
            field=django_jalali.db.models.jDateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='end_date',
            field=django_jalali.db.models.jDateTimeField(),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='start_date',
            field=django_jalali.db.models.jDateTimeField(),
        ),
        migrations.AlterField(
            model_name='registration',
            name='_created_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='_updated_at',
            field=django_jalali.db.models.jDateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='next_payment_date',
            field=django_jalali.db.models.jDateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='registration_date',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True),
        ),
    ]
