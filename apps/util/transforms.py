from datetime import datetime

from django.utils import timezone

class TimeTransform:
    def __init__(self, time='now', type='unix_time'):
        self.type = type

        if time == 'now':
            self.unix_time = timezone.now()
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