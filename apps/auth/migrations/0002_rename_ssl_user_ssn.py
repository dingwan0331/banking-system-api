# Generated by Django 4.1.3 on 2022-11-29 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='ssl',
            new_name='ssn',
        ),
    ]