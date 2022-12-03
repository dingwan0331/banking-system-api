# Generated by Django 4.1.3 on 2022-12-03 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_user_credit'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(('credit__gte', 0)), name='users_credit_not_less_than_zero'),
        ),
    ]