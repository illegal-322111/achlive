from django.urls import path

from . import views

urlpatterns = [
    path('', views.home,name="home"),
    path('category/<slug:category_slug>', views.category_list, name='category_list'),
    path('random_names/', views.trial, name='random_name'),
    path('download/', views.download_csv, name='download'),
]