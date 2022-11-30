import json

import bcrypt
import jwt

from django.views import View
from django.http  import JsonResponse

from .models              import User
from config.settings.base import SECRET_KEY

class UserView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name, ssn, password = data.get('name'), data.get('ssn'), data.get('password')

            hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

            User.objects.create(
                name     = name,
                ssn      = ssn,
                password = hashed_password
            )

            return JsonResponse({'meesage' : 'Success'}, status=201)
        except Exception:
            return JsonResponse({'message' : 'Server Error'}, status=500)

class SigninView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            ssn, password = data.get('ssn'), data.get('password')

            user = User.objects.get(ssn = ssn)

            if not bcrypt.checkpw(password.encode('utf-8'), user.password):
                return JsonResponse({"message" : "Password Invalid"}, status=401)

            access_token = jwt.encode({'id':user.id}, SECRET_KEY)

            return JsonResponse({'access_token' : access_token}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'User does not exist'}, status=400)

        except Exception:
            return JsonResponse({'message' : 'Server Error'}, status=500)