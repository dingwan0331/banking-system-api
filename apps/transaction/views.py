import bcrypt

from django.views           import View
from django.http            import JsonResponse
from django.db              import transaction
from django.db.models       import Q
from django.core.exceptions import ValidationError
from django.db.utils        import IntegrityError

from apps.transaction.models import Transaction, Account
from apps.util.token         import validate_token
from apps.util.transforms    import TimeTransform, GetTransactionsQueryTransform
from apps.util.validators    import PostTransactionsJsonValidator

class TransactionView(View):
    @validate_token
    def post(self, request, account_id):
        '''
        request = {
            password: str,
            summary: str,
            amount: str,
            is_withdrawal: boolean
        }
        '''
        try:
            data = PostTransactionsJsonValidator(request.body)
            user = request.user

            password      = data.password
            is_withdrawal = data.is_withdrawal
            amount        = data.amount
            summary       = data.summary if data.summary else user.last_name + user.first_name

            if account_id == 0:
                return JsonResponse({'message' : 'Invalid account id'})
            
            with transaction.atomic(using='default'):
                account = Account.objects.get(id = account_id)

                if account.user_id != user.id:
                    return JsonResponse({'message' : 'Dont have permission'}, status=403)

                if not bcrypt.checkpw(password.encode('utf-8') , account.password):
                    return JsonResponse({'message' : 'Invalid password'}, status=401)

                balance = account.balance + amount

                if balance < 0:
                    return JsonResponse({'message' : 'Insufficient balance'})

                user.credit -= amount
                user.save()

                transaction_row = Transaction.objects.create(
                    amount        = amount,
                    balance       = balance,
                    timestamp     = TimeTransform().get_now('int_unix_time'),
                    is_withdrawal = is_withdrawal,
                    summary       = summary,
                    account_id    = account_id
                )
 
                account.balance = transaction_row.balance
                account.save()

            result  = {'Balance after transaction': account.balance, 'Transaction amount': transaction_row.amount}
            headers = {'Location': f'/transactions/{transaction_row.id}'}

            return JsonResponse(result,headers = headers, status=201)

        except Account.DoesNotExist:
            return JsonResponse({'message' : 'Does not account'}, status=400)

        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status=400)

        except IntegrityError as e:
            if str(e) == 'CHECK constraint failed: credit':
                return JsonResponse({'mesage' : 'Dont have enough credit'}, status=400)

            return JsonResponse({'message':'Server error'}, status=500)

        except Exception as e:
            
            print(e.__class__)
            return JsonResponse({'message':'Server error'}, status=500)
    
    @validate_token
    def get(self, request, account_id):
        '''
        request = {
            transaction-type : deposit, withdrawal, all
            order_key  : recent, oldest
            offset     : str(positive_int)
            limit      : str(positive_int)
            start_date : ex) '2002-02-02'
            end_date   : ex) '2002-02-02'
        }
        '''
        try:
            query = GetTransactionsQueryTransform(request.GET)
            user  = request.user
            
            offset     = query.offset
            limit      = query.limit
            order_by   = query.order_by
            start_date = query.start_date
            end_date   = query.end_date
            transaction_type = query.transaction_type

            account = Account.objects.get(id = account_id)

            if account.user_id != user.id:
                return JsonResponse({'message' : 'Dont have permission'}, status=403)
            
            q = Q(account_id=account_id)

            ONE_DAY = 86400000000
            
            start_date = TimeTransform(start_date, 'str_date').unix_time_to_int()
            end_date = TimeTransform(end_date, 'str_date').unix_time_to_int() + ONE_DAY

            q &= Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)

            if transaction_type != 'all':
                q &= Q(is_withdrawal = transaction_type == 'withdrawal')

            transaction_rows = Transaction.objects.filter(q).order_by(order_by)[offset: offset+limit]

            result = [
                {
                    'amount'        : transaction.amount,
                    'balance'       : transaction.balance,
                    'summary'       : transaction.summary,
                    'timestamp'     : TimeTransform(transaction.timestamp, 'int_unix_time').make_aware(),
                    'is_withdrawal' : transaction.is_withdrawal
                } for transaction in transaction_rows
            ]

            return JsonResponse({'transactions':result}, status=200)

        except ValidationError as e:
            return JsonResponse({'message': e.message}, status=400)
        
        except Account.DoesNotExist:
            return JsonResponse({'message' : 'Invalid account id'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message':'Server error'}, status=500)
        
