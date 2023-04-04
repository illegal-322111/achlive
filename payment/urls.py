from django.urls import path
from . import views

app_name="payment"

urlpatterns=[
    path('create/<pk>', views.create_payment, name='create_payment'),
    path('invoice/<pk>',views.track_invoice, name='track_payment'),
    path('receive/', views.receive_payment, name='receive_payment'),
    path('buy/<int:pk>', views.buy, name='buy'),
    path('balance/create/', views.add_balance, name='create_balance'),
    path('balance/<int:pk>',views.track_balance, name='track_balance'),
    path('balance/receive/', views.receive_balance, name='receive_balance'),
]