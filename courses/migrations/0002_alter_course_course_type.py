# Generated by Django 5.2.1 on 2025-06-04 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_type',
            field=models.CharField(choices=[(1, 'دوره\u200cهای پیشوایی'), (2, 'دوره\u200cهای رابطه'), (3, 'دوره\u200cهای مواجهه'), (4, 'تحویل سال دگرگون'), (5, 'جان کلام'), (6, 'پویش'), (7, 'پیله')], default='دوره\u200cهای پیشوایی', max_length=50),
        ),
    ]
