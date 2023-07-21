from django.urls import path
from . import views

app_name="payment"

urlpatterns=[
    path('buy/<int:pk>', views.buy, name='buy'),
    path('card/purchase',views.cards, name="cards"),
    path('coinbase', views.create_coinbase_payment, name="coinbase"),
    path('verify', views.coinbase_webhook, name="coinbase_check"),
]