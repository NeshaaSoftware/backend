# Generated by Django 5.2.4 on 2025-07-04 21:21

import django.utils.timezone
import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_crmlog_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crmlog',
            name='date',
            field=django_jalali.db.models.jDateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
