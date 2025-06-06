# Generated by Django 5.2.1 on 2025-06-04 16:36

import commons.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_created_at', models.DateTimeField(auto_now_add=True)),
                ('_updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('invoice_number', models.CharField(blank=True, max_length=50, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField()),
                ('person', models.CharField(blank=True, max_length=100, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_paid', models.BooleanField(default=False)),
                ('cost_type', models.CharField(choices=[('اقامت هتل - ثابت', 'اقامت هتل - ثابت'), ('پذیرایی تیم اجرایی - ثابت', 'پذیرایی تیم اجرایی - ثابت'), ('جابجایی تیم اجرایی - ثابت', 'جابجایی تیم اجرایی - ثابت'), ('تجهیزات - ثابت', 'تجهیزات - ثابت'), ('نیروی خدماتی - ثابت', 'نیروی خدماتی - ثابت'), ('جبران خدمات تیم اجرا - ثابت', 'جبران خدمات تیم اجرا - ثابت'), ('لوازم تحریر - متغیر', 'لوازم تحریر - متغیر'), ('پذیرایی - متغیر', 'پذیرایی - متغیر')], max_length=50)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='courses.course')),
            ],
            options={
                'verbose_name': 'Cost',
                'verbose_name_plural': 'Costs',
                'ordering': ['-date', '-_created_at'],
            },
            bases=(models.Model,),
        ),
    ]
