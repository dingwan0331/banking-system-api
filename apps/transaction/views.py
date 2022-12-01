import json

import bcrypt

from django.views import View
from django.http  import JsonResponse
from django.utils import timezone
from django.db    import transaction

from apps.transaction.models import Transaction, Account
from apps.util.token         import validate_token

class TransactionView(View):
    @validate_token
    def post(self, request):
        '''
        request = {
            account_id: int,
            password: str,
            summary: str,
            amount: int,
        }
        '''
        try:
            data = json.loads(request.body)
            user = request.user

            account_id = data['account_id']
            password   = data['password']
            amount     = data['amount']
            summary    = data.get('summary',user.name)
            
            with transaction.atomic(using='default'):
                account = Account.objects.get(id = account_id)

                if account.user_id != user.id:
                    return JsonResponse({'message' : 'Dont have permission'}, status=403)

                if not bcrypt.checkpw(password.encode('utf-8') , account.password):
                    return JsonResponse({'message' : 'Invalid password'}, status=401)

                deposit = Transaction.objects.create(
                    amount        = amount,
                    balance       = account.balance + amount,
                    timestamp     = timezone.now().timestamp(),
                    is_withdrawal = False,
                    summary       = summary,
                    account_id    = account_id
                )
                account.balance = deposit.balance
                account.save()

            result = {'Balance after transaction': account.balance, 'Transaction amount': amount}

            return JsonResponse(result, status=201)

        except Account.DoesNotExist:
            return JsonResponse({'message' : 'Does not account'}, status=400)

        except KeyError:
            return JsonResponse({'message' : 'Key error'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message':'Server error'}, status=500)