from django.db import models

from apps.util.models import TimeStampModel

class User(TimeStampModel):
    first_name         = models.CharField(max_length=5)
    last_name          = models.CharField(max_length=5)
    username           = models.CharField(max_length=10, unique=True)
    password           = models.BinaryField(max_length=60)

    class Meta():
        db_table = 'users'
    
    def __str__(self):
        return f'{self.name} ({self.pk})'