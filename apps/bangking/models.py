from django.db import models

from apps.util.models import TimeStampModel

# Create your models here.

class Account(TimeStampModel):
    account_number = models.CharField(max_length=200)
    balance        = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta():
        db_table = 'accounts'

class AccountType(models.Model):
    id   = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=10)

    class Meta():
        db_table = 'account_types'

class TransactionHistory(models.Model):
    amount        = models.DecimalField(max_digits=19, decimal_places=4)
    balance       = models.DecimalField(max_digits=19, decimal_places=4)
    is_withdrawal = models.BooleanField()
    timestamp     = models.DateTimeField(auto_now_add=True)
    summary       = models.CharField(max_length=50)

    class Meta():
        db_table = 'transaction_histories'