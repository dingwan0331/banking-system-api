import bcrypt

from django.views           import View
from django.http            import JsonResponse
from django.db              import transaction
from django.db.models       import Q
from django.db.utils        import IntegrityError

from apps.transaction.models import Transaction, Account
from apps.util.token         import validate_token
from apps.util.transforms    import TimeTransform, GetTransactionsQueryTransform
from apps.util.validators    import PostTransactionsJsonValidator
from apps.util.exceptions    import AuthException, BadRequestException, PermissionException

class TransactionView(View):
    @validate_token
    def post(self, request, account_id):
        '''
        request.body = {
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

            signed_amount =  -amount if is_withdrawal else amount

            if account_id == 0:
                raise BadRequestException('Invalid account id')
            
            with transaction.atomic(using='default'):
                account = Account.objects.get(id = account_id)

                if account.user_id != user.id:
                    raise PermissionException('Dont have permission')

                if not bcrypt.checkpw(password.encode('utf-8') , account.password):
                    raise AuthException('Invalid password')

                balance = account.balance + signed_amount

                if balance < 0:
                    raise PermissionException('Insufficient balance')

                user.credit -= signed_amount
                user.save()

                transaction_row = Transaction.objects.create(
                    amount        = amount,
                    balance       = balance,
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
            raise BadRequestException('Does not account')

        except IntegrityError as e:
            if str(e) == 'CHECK constraint failed: credit':
                raise BadRequestException('Dont have enough credit')
            raise
    
    @validate_token
    def get(self, request, account_id):
        '''
        request.GET = {
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
                raise PermissionException('Dont have permission')
            
            q = Q(account_id=account_id)

            q &= Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)

            if transaction_type != 'all':
                q &= Q(is_withdrawal = transaction_type == 'withdrawal')

            transaction_rows = Transaction.objects.filter(q).order_by(order_by)[offset: offset+limit]

            result = [
                {
                    'amount'        : transaction.amount,
                    'balance'       : transaction.balance,
                    'summary'       : transaction.summary,
                    'timestamp'     : TimeTransform(transaction.timestamp).make_aware(),
                    'is_withdrawal' : transaction.is_withdrawal
                } for transaction in transaction_rows
            ]

            return JsonResponse({'transactions':result}, status=200)
        
        except Account.DoesNotExist:
            raise BadRequestException('Invalid account id')