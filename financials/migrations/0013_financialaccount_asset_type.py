# Generated by Django 5.2.4 on 2025-07-18 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0012_alter_coursetransaction_transaction_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialaccount',
            name='asset_type',
            field=models.IntegerField(choices=[(1, 'ریال'), (2, 'صندوق درآمد ثابت'), (3, 'رمز ارز'), (4, 'ارز')], default=1, help_text='نوع دارایی'),
        ),
    ]
