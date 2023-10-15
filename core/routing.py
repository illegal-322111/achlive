from payment import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/achlive/$', consumers.CoinbaseWebsocketConsumer.as_asgi()),
]
