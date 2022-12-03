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
            first_name = '길동',
            last_name  = '홍',
            username   = 'user1',
            password   = hashed_password,
            credit     = 1000000
            )

        user2 = User.objects.create(
            first_name = '병동',
            last_name  = '백',
            username   = 'user2',
            password   = hashed_password,
            credit     = 1000000
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
            'password'      : '1234',
            'summary'       : '예금하기',
            'amount'        : '10000',
            'is_withdrawal' : False
            }
        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {
            'Balance after transaction' : '110000.0000', 
            'Transaction amount'        : 10000
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Location'],'/transactions/1')

    def test_deposit_success_case_without_summary(self):
        request_body = {
            'password'      : '1234',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {
            'Balance after transaction' : '110000.0000', 
            'Transaction amount'        : 10000
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Location'],'/transactions/1')

    def test_deposit_fail_case_wrong_password(self):
        request_body = {
            'password'      : '1231',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {'message': 'Invalid password'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 401)

    def test_deposit_fail_case_dont_have_permission(self):
        request_body = {
            'password'      : '1231',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/2/transactions', request_body, **headers)

        expected_response = {'message': 'Dont have permission'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 403)

    def test_deposit_fail_case_key_error_without_amount(self):
        request_body = {
            'password'      : '1231',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {'message': 'Invalid amount'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_key_error_without_password(self):
        request_body = {
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {'message': 'Invalid password'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 401)

    def test_deposit_fail_case_key_error_without_is_withdrawal(self):
        request_body = {
            'amount'     : '10000',
            'password'   : '1231',
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {'message': 'Invalid is_withdrawal'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_without_access_token(self):
        headers = {'content_type' : 'application/json'}

        response = client.post('/accounts/1/transactions',  **headers)

        expected_response = {'message': 'Invalid token'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 401)

    def test_deposit_fail_case_amount_lower_zero(self):
        request_body = {
            'password'      : '1234',
            'summary'       : '예금하기',
            'amount'        : '-10000',
            'is_withdrawal' : False
            }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {'message' : 'Invalid amount'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_deposit_fail_case_path_params_not_int(self):
        request_body = { 
            'password'      : '1231',
            'amount'        : '10000',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/asa/transactions', request_body, **headers)

        self.assertEqual(response.status_code, 404)