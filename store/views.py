from django.shortcuts import render, get_object_or_404
from .models import *
from payment.models import *
from django.contrib.auth.decorators import login_required
@login_required
def home(request):
    invoice = Invoice.objects.filter(created_by=request.user).first()
    return render(request,"home.html",context={"invoice":invoice})

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'category.html', {'category': category, 'products': products})