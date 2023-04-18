from .models import Category
from django.contrib.auth.decorators import login_required
from payment.models import *
def categories(request):
    return{
        'usa': Category.objects.filter(location=0),   
        'canada': Category.objects.filter(location=1),  
        'europe': Category.objects.filter(location=2),  
        'pua': Category.objects.filter(location=3),  
        'categories': Category.objects.filter(location=-1),
        'category': Category.objects.all()
    }

def balance(request):
    if request.user.is_authenticated:
        balance = Balance.objects.filter(created_by=request.user)
        b = round(balance, 2)
        return {'balance': b}
    else:
        b = 0.00
        return {'balance': b}