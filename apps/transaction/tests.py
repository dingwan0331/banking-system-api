import bcrypt
import jwt

from decimal   import *
from freezegun import freeze_time

from django.test  import TestCase, Client
from django.utils import timezone

from apps.transaction.models import Transaction, Account, AccountType
from apps.auth.models        import User
from config.settings.base    import SECRET_KEY

client          = Client()
balance         = Decimal('100000.0000')
access_token    = jwt.encode({'id':1}, SECRET_KEY)
password        = '1234'
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
sample_binary   = b'111'

class TransactionViewTest(TestCase):
    def setUp(self):        
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

class GetTransactionsTest(TestCase):
    def setUp(self):        
        self.freezer = freeze_time('2022-10-30')
        self.freezer.start()
        
        user = User.objects.create(
            first_name = '길동',
            last_name  = '홍',
            username   = 'user1',
            password   = hashed_password,
            credit     = 10000000000000
            )

        AccountType.objects.create(name = '일반예금')

        BALANCE = 10000000000000

        account = Account.objects.create(
            account_number = sample_binary,
            password       = hashed_password,
            balance        = BALANCE,
            type_id        = 1,
            user           = user
        )

        transactions = []

        amount = 10000

        for i in range(1,101):
            timedelta         = timezone.timedelta(days=i)
            now               = timezone.datetime(2022,10,30)
            summary           = user.last_name + user.first_name
            int_unix_time     = (now - timedelta).timestamp() * 1000000

            if i%2 ==0:
                BALANCE -= amount
                is_withdrawal = True
            else:
                BALANCE += amount
                is_withdrawal = False

            transactions.append(
                Transaction(
                    is_withdrawal = is_withdrawal, 
                    account       = account,
                    summary       = summary, 
                    timestamp     = int_unix_time,
                    amount        = amount,
                    balance       = BALANCE
                )
            )

        Transaction.objects.bulk_create( transactions )

    def tearDown(self):
        Transaction.objects.all().delete()
        Account.objects.all().delete()
        AccountType.objects.all().delete()
        User.objects.all().delete()
        self.freezer.stop()

    def test_success_case_쿼리파라미터_없이_요청(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions', **headers)

        expected_response = [
            {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-29T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-28T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-27T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-26T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-25T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-24T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-23T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-22T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-21T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-20T00:00:00+09:00',
                    'is_withdrawal' : True
            }
        ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_success_case_쿼리파라미터_limit_3(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?limit=3', **headers)

        expected_response = [
            {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-29T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-28T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-27T00:00:00+09:00',
                    'is_withdrawal' : False
            }
        ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

        

    def test_success_case_쿼리파라미터_offset_3(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?offset=3', **headers)

        expected_response = [
            {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-26T00:00:00+09:00',
                    'is_withdrawal' : True
            },            {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-25T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-24T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-23T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-22T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-21T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-20T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-19T00:00:00+09:00',
                    'is_withdrawal' : False
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-18T00:00:00+09:00',
                    'is_withdrawal' : True
            },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-17T00:00:00+09:00',
                    'is_withdrawal' : False
            }
        ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)