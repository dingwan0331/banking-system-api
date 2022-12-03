from django.db    import models

from apps.util.models     import TimeStampModel
from apps.util.transforms import TimeTransform

# Create your models here.
def time_now():
    now = TimeTransform().unix_time_to_int()
    return now

class Account(TimeStampModel):
    account_number = models.BinaryField(max_length=256)
    balance        = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    password       = models.BinaryField(max_length=60)
    user           = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    type           = models.ForeignKey('AccountType', on_delete=models.PROTECT)

    class Meta():
        db_table = 'accounts'
        constraints= [
            models.CheckConstraint(name='accounts_balance_not_less_than_zero', check=models.Q(balance__gte=0)),
        ]

class AccountType(models.Model):
    id   = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=10)

    class Meta():
        db_table = 'account_types'

class Transaction(models.Model):
    amount        = models.DecimalField(max_digits=19, decimal_places=4)
    balance       = models.DecimalField(max_digits=19, decimal_places=4)
    is_withdrawal = models.BooleanField()
    timestamp     = models.PositiveBigIntegerField(default=time_now)
    summary       = models.CharField(max_length=20)
    account       = models.ForeignKey('Account', on_delete=models.PROTECT)

    class Meta():
        db_table = 'transactions'
        index_together = ['account', 'timestamp']
        constraints= [
            models.CheckConstraint(name='tansactions_amount_not_less_than_zero', check=models.Q(amount__gte=0)),
            models.CheckConstraint(name='tansactions_balance_not_less_than_zero', check=models.Q(balance__gte=0)),
            models.CheckConstraint(
                name='timestamp_not_more_than_now', 
                check=models.Q(
                    timestamp__lte = 1000000 * (models.Func( models.functions.Now(), function="UNIXEPOCH")+10)
                    )
                )
            ]