from django.db import models

from apps.util.models import TimeStampModel
# Create your models here.

class Account(TimeStampModel):
    account_number = models.BinaryField(max_length=256)
    balance        = models.DecimalField(max_digits=19, decimal_places=4)
    password       = models.BinaryField(max_length=60)
    user           = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    type           = models.ForeignKey('AccountType', on_delete=models.PROTECT)

    class Meta():
        db_table = 'accounts'

class AccountType(models.Model):
    id   = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=10)

    class Meta():
        db_table = 'account_types'

class Transaction(models.Model):
    amount        = models.DecimalField(max_digits=19, decimal_places=4)
    balance       = models.DecimalField(max_digits=19, decimal_places=4)
    is_withdrawal = models.BooleanField()
    timestamp     = models.PositiveBigIntegerField()
    summary       = models.CharField(max_length=20)
    account       = models.ForeignKey('Account', on_delete=models.PROTECT)

    class Meta():
        db_table = 'transactions'