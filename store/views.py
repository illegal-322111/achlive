from django.shortcuts import render, get_object_or_404, HttpResponse
from .models import *
from payment.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .context_processors import random_name
from django.http import FileResponse
from django.conf import settings
import os
from account.models import *

def home(request):
    if request.user.is_authenticated:
        invoice = Invoice.objects.filter(created_by=request.user).first()
        extraction = Invoice.objects.filter(created_by=request.user, product__name = "Decryptor")
        if extraction.exists():
            user = request.user
            user.verified = True
            user.save()
        else:
            product = Product.objects.get(name="Decryptor")
            context = {
                "product" : product
            }
            return render(request, "extraction.html", context) 
        return render(request,"home.html",context={"invoice":invoice})
    return render(request,"home.html")

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'category.html', {'category': category, 'products': products})

def trial(request):
    
    return JsonResponse(random_name(request))

def download_csv(request):
    file_name = 'output.csv'  # Name of the CSV file
    file_path = os.path.join(settings.STATICFILES_DIRS[0], file_name)  # Replace with the actual path to the exported CSV file

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            file_content = file.read()  # Read file contents into memory
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response.write(file_content)  # Write the file content to the response
        return response
    else:
        return HttpResponse('File not found.')