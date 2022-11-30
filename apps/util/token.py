import jwt

from django.http import JsonResponse

from apps.auth.models        import User
from config.settings.base import SECRET_KEY

def validate_token(func):
    def wrapper(self,request,*args,**kwargs):
        try:
            access_token = request.headers.get("Authorization",None)
            payload = jwt.decode(access_token, SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['id'])
            request.user = user  
            
            return func(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'Invalid token'}, status=401)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'Invalid token'}, status=401)

    return wrapper