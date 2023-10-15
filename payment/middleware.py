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
        
# wallet_api/middleware.py

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from account.models import Customer

@database_sync_to_async
def get_user(user_id):
    try:
        return Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        return AnonymousUser()

class SimpleWebSocketAuthMiddleware:
    """
    Custom middleware that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(param.split('=') for param in query_string.split('&'))
        user_id = query_params.get('user_id')

        if user_id:
            scope['user'] = await get_user(int(user_id))
        else:
            scope['user'] = AnonymousUser()

        # Call the next middleware or consumer
        return await self.app(scope, receive, send)


