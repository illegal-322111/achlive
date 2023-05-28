from .models import Category
from django.contrib.auth.decorators import login_required
from payment.models import *
import random
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
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance and balance.balance is not None:
            b = round(balance.balance, 2)
            return {'balance': b}
        else:
            b = 0.00
            return {'balance': b}
    else:
        b = 0.00
        return {'balance': b}
    
def random_name(request):
    names = ['Kolaskov','Mclean', 'Trevor', 'Rexxy', 'Sarah', 'David', 'Draven', 'Raven', 'Malachi', 'Lilith', 'Azazel', 'Morgana', 'Damien', 'Bellatrix', 'Lucius', 'Luna', 'Salem', 'Morticia', 'Vladimir', 'Selene', 'Spike','Devon']
    bank_names = ['Bank of America', 'Chase', 'Wells Fargo', 'Citibank', 'US Bank', 'Citizens', 'TD Bank', 'Hutington Bank', 'Woodforest Bank', 'Zelle', 'Chime']
    name = random.choice(names)
    bank_name = random.choice(bank_names)
    
    data = {
        'human_name': name,
        'bank_name': bank_name,
    }
    
    return data