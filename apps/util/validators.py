import re
import json

from apps.util.exceptions import AuthException, BadRequestException

class PostTransactionsJsonValidator:
    def __init__(self, body_json):
        data = json.loads(body_json)

        self.password      = data.get('password', '')
        self.summary       = data.get('summary', '')
        self.amount        = data.get('amount', '')
        self.is_withdrawal = data.get('is_withdrawal', '')

        self.__validate()

    def __validate(self):
        self.__validate_is_withdrawal()
        self.__validate_password()
        self.__validate_amount()
        self.__validate_summary()

    def __validate_password(self):
        PASSWORD_REGEX = '\d{4}'
        
        if not re.fullmatch(PASSWORD_REGEX, self.password):
            raise AuthException('Invalid password')            

    def __validate_is_withdrawal(self):
        if type(self.is_withdrawal) != bool:
            raise BadRequestException('Invalid is_withdrawal')
    
    def __validate_summary(self):
        if self.summary and type(self.summary) != str:
            raise BadRequestException('Invalid summary')

    def __validate_amount(self):
        AMOUNT_REGEX = '^[1-9]+(\.?[0-9]+)?$'
            
        if not re.fullmatch(AMOUNT_REGEX,self.amount):
            raise BadRequestException('Invalid amount')

        self.amount = int(self.amount)