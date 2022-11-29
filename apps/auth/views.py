import json

import bcrypt
import jwt

from django.views import View
from django.http  import JsonResponse

from .models         import User

class SigninView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            ssn, password = data.get('ssn'), data.get('password')

            user = User.objects.get(ssn = ssn)

            if not bcrypt.checkpw(password.encode('utf-8'), user.password):
                return JsonResponse({"message" : "Password Invalid"}, status=401)

            access_token = jwt.encode({'id':user.id}, 'SECRET_KEY')

            return JsonResponse({'access_token' : access_token}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'User does not exist'}, status=400)

        except Exception:
            return JsonResponse({'message' : 'Server Error'}, status=500)