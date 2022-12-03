import re

from datetime               import datetime
from dateutil.relativedelta import relativedelta

from django.utils           import timezone
from django.core.exceptions import ValidationError

class TimeTransform:
    def __init__(self, time='now', type='unix_time'):
        self.type = type

        if time == 'now':
            self.unix_time = timezone.now().timestamp()
        elif type == 'str_date':
            self.unix_time = datetime.strptime(time, "%Y-%m-%d").timestamp()
        elif type == 'int_unix_time':
            self.unix_time = time / 1000000
        elif type == 'unix_time':
            self.unix_time = time
        elif type == 'datetime':
            self.unix_time = time.timestamp()
        else:
            raise TypeError('Unsupported type')

    def unix_time_to_int(self):
        self.unix_time *= 1000000
        return self.unix_time
    
    def make_aware(self):
        return timezone.make_aware(datetime.fromtimestamp(self.unix_time))
    
    def get_now(self, type='unix_time'):
        now = timezone.now().timestamp()
        if type == 'str_date':
            return datetime.fromtimestamp(now).strftime('%Y-%m-%d')
        elif type == 'int_unix_time':
            return now * 1000000
        elif type == 'unix_time':
            return now
        elif type == 'datetime':
            return datetime.fromtimestamp(now)
        else:
            raise TypeError('Unsupported type')

class GetTransactionsQueryTransform:
    __order_set        = {'recent' : '-timestamp', 'oldest' : 'timestamp'}
    __transaction_type = ['deposit', 'withdrawal', 'all']
    
    def __init__(self, query):
        self.start_date       = query.get('start-date')
        self.end_date         = query.get('end-date')
        self.order_by         = query.get('order-key', 'recent')
        self.offset           = query.get('offset', '0')
        self.limit            = query.get('limit', '10')
        self.transaction_type = query.get('transaction-type', 'all')

        self.translate()

    def translate(self):
        self.__set_offset()
        self.__set_limit()
        self.__set_order_by()
        self.__validate_transaction_type()
        self.__set_start_date()
        self.__set_end_date()

    def __set_offset(self):
        OFFSEET_REGEX = '\d'
        if not re.fullmatch(OFFSEET_REGEX, self.offset):
            raise ValidationError('Invalid offset')
        
        self.offset = int(self.offset)
    
    def __set_limit(self):
        LIMIT_REGEX = '^[^0]\d*'

        if not re.fullmatch(LIMIT_REGEX, self.limit):
            raise ValidationError('Invalid limit')

        self.limit = int(self.limit)
    
    def __set_order_by(self):
        try:
            self.order_by = self.__order_set[self.order_by]
        except KeyError:
            raise ValidationError('Invalid order key')

    def __validate_transaction_type(self):
        if self.transaction_type not in self.__transaction_type:
            raise ValidationError('Invalid transaction type')
    
    def __set_start_date(self):
        DATE_REGEX = '(19|20)\d{2}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])'
        if not self.start_date:
            self.start_date = (TimeTransform().get_now('datetime') - relativedelta(months=3)).strftime('%Y-%m-%d')
            
        if not re.fullmatch(DATE_REGEX, self.start_date):
            raise ValidationError('Invalid start date')
            
    def __set_end_date(self):
        DATE_REGEX = '(19|20)\d{2}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])'
        if not self.end_date:
            self.end_date = TimeTransform().get_now('str_date')

        if not re.fullmatch(DATE_REGEX, self.end_date):
            raise ValidationError('Invalid end date')