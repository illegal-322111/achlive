from django.http import HttpResponseForbidden

class AllowNoRefererMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'HTTP_REFERER' not in request.META:
            # Allow the request even if there is no Referer header
            return None
        else:
            # Otherwise, proceed with the normal behavior
            return None
