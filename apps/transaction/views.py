import json
import re

import bcrypt

from django.views import View
from django.http  import JsonResponse
from django.utils import timezone
from django.db    import transaction

from apps.transaction.models import Transaction, Account
from apps.util.token         import validate_token

class TransactionView(View):
    @validate_token
    def post(self, request, account_id):
        '''
        request = {
            account_id: str,
            password: str,
            summary: str,
            amount: str,
            is_withdrawal: boolean
        }
        '''
        try:
            data = json.loads(request.body)
            user = request.user

            password      = data['password']
            is_withdrawal = data['is_withdrawal']
            amount        = data['amount']
            summary       = data.get('summary',user.name)

            PASSWORD_REGEX   = '\d{4}'
            AMOUNT_REGEX     = '^[1-9]+(\.?[0-9]+)?$'
                
            if not re.fullmatch(AMOUNT_REGEX,amount):
                return JsonResponse({'message' : 'Invalid amount'}, status=400)
            
            if account_id == 0:
                return JsonResponse({'message' : 'Invalid account_id'})

            if type(is_withdrawal) != bool:
                return JsonResponse({'message' : 'Invalid is_withdrawal'})
            
            if type(summary) != str:
                return JsonResponse({'message' : 'Invalid summary'})

            if not re.fullmatch(PASSWORD_REGEX,password):
                return JsonResponse({'message' : 'Invalid password'})

            signed_amount = -int(amount) if is_withdrawal else int(amount)
            
            with transaction.atomic(using='default'):
                account = Account.objects.get(id = account_id)

                if account.user_id != user.id:
                    return JsonResponse({'message' : 'Dont have permission'}, status=403)

                if not bcrypt.checkpw(password.encode('utf-8') , account.password):
                    return JsonResponse({'message' : 'Invalid password'}, status=401)

                balacne = account.balance + signed_amount

                if balacne < 0:
                    return JsonResponse({'message' : 'Insufficient balance'})

                transaction_row = Transaction.objects.create(
                    amount        = amount,
                    balance       = balacne,
                    timestamp     = timezone.now().timestamp() * 1000000,
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

        except KeyError:
            return JsonResponse({'message' : 'Key error'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message':'Server error'}, status=500)