# Generated by Django 4.1.3 on 2022-11-30 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0002_transaction_account_password_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='date',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='time',
        ),
        migrations.AddField(
            model_name='transaction',
            name='timestamp',
            field=models.PositiveBigIntegerField(default=0),
            preserve_default=False,
        ),
    ]