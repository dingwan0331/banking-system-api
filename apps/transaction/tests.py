import bcrypt
import jwt

from decimal import *

from django.test import TestCase, Client

from .models              import Transaction, Account, AccountType
from ..auth.models        import User
from config.settings.base import SECRET_KEY

balance = Decimal('100000.0000')

class DepositViewTest(TestCase):
    def setUp(self):
        password = '1234'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sample_binary = b'111'
        
        User.objects.create(
            name     = '홍길동',
            ssn      = sample_binary,
            password = hashed_password
            )

        AccountType.objects.create(name = '일반예금')

        Account.objects.create(
            account_number = sample_binary,
            password       = hashed_password,
            balance        = balance,
            type_id        = 1,
            user_id        = 1
        )
    
    def tearDown(self):
        Transaction.objects.all().delete()
        Account.objects.all().delete()
        AccountType.objects.all().delete()
        User.objects.all().delete()

    def test_deposit_success_case(self):
        client       = Client()
        access_token = jwt.encode({'id':1}, SECRET_KEY)
        
        request_body = { 
            'account_id' : 1,
            'password'   : '1234',
            'summary'    : '예금하기',
            'amount'     : 10000,
            }
        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions/deposit', request_body, **headers)

        expected_response = {
            'Balance after transaction' : str(balance + request_body['amount']), 
            'Transaction amount'        : request_body['amount']
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)