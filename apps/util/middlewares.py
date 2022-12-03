from django.http import JsonResponse

class ErrorResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_exception(self, request, exception):
        try:
            if exception.is_custom:
                return JsonResponse({'message' : exception.message}, status=exception.status)

        except:
            return JsonResponse({'message' : 'Server error'}, status=500)