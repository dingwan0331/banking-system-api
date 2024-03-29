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
            credit     = 50000
            )

        user2 = User.objects.create(
            first_name = '병동',
            last_name  = '백',
            username   = 'user2',
            password   = hashed_password,
            credit     = 500000
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

    def test_withdrawal_success_case(self):        
        request_body = {
            'password'      : '1234',
            'summary'       : '예금하기',
            'amount'        : '10000',
            'is_withdrawal' : True
            }
            
        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {
            'Balance after transaction' : '90000.0000', 
            'Transaction amount'        : 10000
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Location'],'/transactions/1')

    def test_withdrawal_success_case_without_summary(self):
        request_body = {
            'password'      : '1234',
            'amount'        : '10000',
            'is_withdrawal' : True
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {
            'Balance after transaction' : '90000.0000', 
            'Transaction amount'        : 10000
            }

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Location'],'/transactions/1')

    def test_deposit_fail_case_amount_over_users_credit(self):
        request_body = {
            'password'      : '1234',
            'amount'        : '50001',
            'is_withdrawal' : False
        }

        headers = {
            'HTTP_Authorization' : access_token,
            'content_type'       :'application/json'
        }

        response = client.post('/accounts/1/transactions', request_body, **headers)

        expected_response = {'message' : 'Dont have enough credit'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

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
            int_unix_time     = (now - timedelta).timestamp()

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

    def test_success_case_dont_have_query(self):
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

    def test_success_case_query_limit_3(self):
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

        

    def test_success_case_query_offset_3(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?offset=3', **headers)

        expected_response = [
                {
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

    def test_success_case_query_offset_4_limit_2(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?offset=4&limit=2', **headers)

        expected_response = [
                {
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
                },
            ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_success_case_query_order_key_recent(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?order-key=recent', **headers)

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

    def test_success_case_query_order_key_oldest(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?order-key=oldest', **headers)

        expected_response = [
                {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-07-30T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-07-31T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-01T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-02T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-03T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-04T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-05T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-06T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-07T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-08-08T00:00:00+09:00',
                    'is_withdrawal' : False
                },
            ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_success_case_query_start_date_20221028(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?start-date=2022-10-28', **headers)

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
                }
            ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)


    def test_success_case_query_end_date_20221001(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?end-date=2022-10-01', **headers)

        expected_response = [
                {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-02T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-01T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-30T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-29T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-28T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-27T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-26T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-25T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-24T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-09-23T00:00:00+09:00',
                    'is_withdrawal' : False
                }
            ]
            
        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_success_case_query_transaction_type_all(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?transaction-type=all', **headers)

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

    def test_success_case_query_transaction_type_deposit(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?transaction-type=deposit', **headers)

        expected_response = [
                {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-29T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-27T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-25T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-23T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-21T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-19T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-17T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-15T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-13T00:00:00+09:00',
                    'is_withdrawal' : False
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000010000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-11T00:00:00+09:00',
                    'is_withdrawal' : False
                }
            ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_success_case_query_transaction_type_withdrawal(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?transaction-type=withdrawal', **headers)

        expected_response = [
                {
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-28T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-26T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-24T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-22T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-20T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-18T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-16T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-14T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-12T00:00:00+09:00',
                    'is_withdrawal' : True
                },{
                    'amount'        : '10000.0000',
                    'balance'       : '10000000000000.0000',
                    'summary'       : '홍길동',
                    'timestamp'     : '2022-10-10T00:00:00+09:00',
                    'is_withdrawal' : True
                }
            ]

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_fail_case_query_start_date_over_end_date(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?start-date=2022-10-11&end-date=2022-10-01', **headers)

        expected_response = []

        self.assertEqual(response.json(), {'transactions' : expected_response})
        self.assertEqual(response.status_code, 200)

    def test_fail_case_query_start_date_before_1900(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?start-date=1899-10-11', **headers)

        expected_response = {'message' : 'Invalid start date'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)

    def test_fail_case_query_start_date_before_1900(self):
        headers = {'HTTP_Authorization' : access_token,}

        response = client.get('/accounts/1/transactions?start-date=2022-13-11', **headers)

        expected_response = {'message' : 'Invalid start date'}

        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, 400)