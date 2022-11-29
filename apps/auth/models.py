from django.db import models

from apps.util.models import TimeStampModel

class User(TimeStampModel):
    name     = models.CharField(max_length=10)
    password = models.BinaryField(max_length=60)
    ssn      = models.BinaryField(max_length=256)

    class Meta():
        db_table = 'users'
    
    def __str__(self):
        return f'{self.name} ({self.pk})'