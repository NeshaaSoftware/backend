# Generated by Django 5.2.4 on 2025-07-18 13:27

import django_jalali.db.models
import jdatetime
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0010_remove_coursetransaction_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursetransaction',
            name='transaction_date',
            field=django_jalali.db.models.jDateTimeField(db_index=True, default=jdatetime.datetime.now, help_text='تاریخ تراکنش'),
        ),
    ]
