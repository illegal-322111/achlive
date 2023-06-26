from django.urls import path

from . import views

urlpatterns = [
    path('', views.home,name="home"),
    path('category/<slug:category_slug>', views.category_list, name='category_list'),
    path('random_names/', views.trial, name='random_name'),
    path('download/', views.download_csv, name='download'),
    path('download/balance/', views.download_balance, name='download_balance'),
    path('download/invoice/', views.download_invoice, name='download_invoice'),
    path('download/users/', views.download_users, name='download_users'),
    path('download/category/', views.download_category, name='download_category'),
]