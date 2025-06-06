# Generated by Django 5.2.1 on 2025-06-04 17:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0004_remove_income_invoice_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='is_received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='income',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='income',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
    ]
