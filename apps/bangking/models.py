from django.db import models

from apps.util.models import TimeStampModel

# Create your models here.

class Account(TimeStampModel):
    account_number = models.CharField(max_length=200)
    balance        = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta():
        db_table = 'accounts'