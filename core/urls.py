from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from account.forms import (UserLoginForm)
urlpatterns = [
    path('longi/', admin.site.urls),
    path('', include('store.urls')),
    path('account/', include('account.urls', namespace="account")),
    path('pay/', include('payment.urls', namespace="payment")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)