# Generated by Django 5.2.4 on 2025-07-29 21:17

import commons.utils
import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_crmlog_date_alter_smslog_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crmlog',
            name='date',
            field=django_jalali.db.models.jDateTimeField(blank=True, db_index=True, default=commons.utils.get_jdatetime_now_with_timezone),
        ),
        migrations.AlterField(
            model_name='smslog',
            name='date',
            field=django_jalali.db.models.jDateTimeField(blank=True, db_index=True, default=commons.utils.get_jdatetime_now_with_timezone),
        ),
    ]
