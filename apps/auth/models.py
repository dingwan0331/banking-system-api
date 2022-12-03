from django.db import models

from apps.util.models import TimeStampModel

class User(TimeStampModel):
    first_name = models.CharField(max_length=5)
    last_name  = models.CharField(max_length=5)
    username   = models.CharField(max_length=10, unique=True)
    password   = models.BinaryField(max_length=60)
    credit     = models.PositiveIntegerField(default=0)

    class Meta():
        db_table = 'users'
        constraints= [
            models.CheckConstraint(name='users_credit_not_less_than_zero', check=models.Q(credit__gte=0)),
        ]
        
    def __str__(self):
        return f'{self.name} ({self.pk})'