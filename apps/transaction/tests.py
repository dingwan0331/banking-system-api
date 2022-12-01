import bcrypt
import jwt

from decimal import *

from django.test import TestCase, Client

from apps.transaction.models import Transaction, Account, AccountType
from apps.auth.models        import User
from config.settings.base    import SECRET_KEY

client       = Client()
balance      = Decimal('100000.0000')
access_token = jwt.encode({'id':1}, SECRET_KEY)

class TransactionViewTest(TestCase):
    def setUp(self):
        password = '1234'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sample_binary = b'111'
        
        user1 = User.objects.create(
            name     = '홍길동',
            ssn      = sample_binary,
            password = hashed_password
            )

        user2 = User.objects.create(
            name     = '백병동',
            ssn      = sample_binary,
            password = hashed_password
            )

        AccountType.objects.create(name = '일반예금')

        Account.objects.create(
            account_number = sample_binary,
            password       = hashed_password,
            balance        = balance,
            type_id        = 1,
            user           = user1
        )
        Account.objects.create(
            account_number = sample_binary,
            password       = hashed_password,
            balance        = balance,
            type_id        = 1,
            user           = user2
        )
    
    def tearDown(self):
        Transaction.objects.all().delete()
        Account.objects.all().delete()
        AccountType.objects.all().delete()
        User.objects.all().delete()

    def test_deposit_success_case(self):        
        request_body = { 
            'account_id'    : '1',
            'password'      : '1234',
            'summary'       : '예금하기',
            'amount'        : '10000',
            'is_withdrawal' : False
            }
        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {
            'Balance after transaction' : str(balance + Decimal(request_body['amount'])), 
            'Transaction amount'        : request_body['amount']
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)

    def test_deposit_success_case_without_summary(self):
        request_body = { 
            'account_id'    : '1',
            'password'      : '1234',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {
            'Balance after transaction' : str(balance + Decimal(request_body['amount'])), 
            'Transaction amount'        : request_body['amount']
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)

    def test_deposit_fail_case_wrong_password(self):
        request_body = { 
            'account_id'    : '1',
            'password'      : '1231',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {'message': 'Invalid password'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 401)

    
    def test_deposit_fail_case_dont_have_permission(self):
        request_body = { 
            'account_id'    : '2',
            'password'      : '1231',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {'message': 'Dont have permission'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 403)

    def test_deposit_fail_case_key_error_without_amount(self):
        request_body = { 
            'account_id'    : '2',
            'password'      : '1231',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {'message': 'Key error'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_key_error_without_account_id(self):
        request_body = { 
            'password'      : '1231',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {'message': 'Key error'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_key_error_without_password(self):
        request_body = { 
            'account_id'    : '2',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {'message': 'Key error'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_key_error_without_is_withdrawal(self):
        request_body = { 
            'account_id' : '2',
            'amount'     : '10000',
            'password'   : '1231',
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/transactions', request_body, **headers)

        expected_response = {'message': 'Key error'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_without_access_token(self):
        headers = {'content_type' : 'application/json'}

        response = client.post('/transactions',  **headers)

        expected_response = {'message': 'Invalid token'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 401)