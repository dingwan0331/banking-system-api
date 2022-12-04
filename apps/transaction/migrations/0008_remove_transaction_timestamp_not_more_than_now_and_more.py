# Generated by Django 4.1.3 on 2022-12-04 18:02

import apps.transaction.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0007_alter_account_balance'),
    ]

    operations = [
        # migrations.RemoveConstraint(
        #     model_name='transaction',
        #     name='timestamp_not_more_than_now',
        # ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.FloatField(default=apps.transaction.models.time_now),
        ),
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.CheckConstraint(check=models.Q(('timestamp__gte', 0)), name='timestamp_not_lower_zero'),
        ),
    ]
