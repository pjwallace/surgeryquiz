from django.shortcuts import redirect

class WWWRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host.lower() == 'testyoursurgery.com':
            return redirect(f'https://www.testyoursurgery.com{request.get_full_path()}', permanent=True)
        response = self.get_response(request)
        return response
