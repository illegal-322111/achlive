from django.urls import path
from . import views

app_name="payment"

urlpatterns=[
    path('buy/<int:pk>', views.buy, name='buy'),
    path('card/purchase',views.cards, name="cards"),
    path('add/', views.add_balance, name="coinbase"),
    path('send/', views.send_mail_kelly, name="send"),
    path('cards/', views.cards_mail, name="notify_cards"),
    path('balance/<int:pk>',views.track_balance, name='track_balance'),
    path('balance/receive/', views.receive_balance, name='receive_balance'),
]