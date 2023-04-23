from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime
import json
import requests
import uuid
import os
from store.models import *
from .models import *
# Create your views here.


def exchanged_rate(amount):
    url = "https://www.blockonomics.co/api/price?currency=USD"
    r = requests.get(url)
    response = r.json()
    return amount/response['price']

def track_invoice(request, pk):
    invoice_id = pk
    invoice = Invoice.objects.get(id=invoice_id)
    data = {
            'order_id':invoice.order_id,
            'bits':invoice.btcvalue/1e8,
            'value':invoice.product.price,
            'addr': invoice.address,
            'status':Invoice.STATUS_CHOICES[invoice.status+1][1],
            'invoice_status': invoice.status,
        }
    if (invoice.received):
        data['paid'] =  invoice.received/1e8
        if (int(invoice.btcvalue) <= int(invoice.received)):
            from_email = "Achlogs@achlive.net"

            to_email = request.user.email
            subject = 'Order confirmation'
            text_content = 'Thank you for the order!'
            html_content = render_to_string('email_notify_customer.html', {'order': invoice.product.pdf.url})

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            invoice.product.Status = False
            invoice.product.save()
            return redirect('account:dashboard')
    else:
        data['paid'] = 0  

    return render(request,'invoice.html',context=data)

def create_payment(request, pk):
    
    product_id = pk
    product = Product.objects.get(id=product_id)
    url = 'https://www.blockonomics.co/api/new_address'
    headers = {'Authorization': "Bearer " + settings.API_KEY}
    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        address = r.json()['address']
        bits = exchanged_rate(product.price)
        order_id = uuid.uuid1()
        invoice = Invoice.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8, product=product, created_by=request.user)
        return HttpResponseRedirect(reverse('payment:track_payment', kwargs={'pk':invoice.id}))
    else:
        print(r.status_code, r.text)
        return HttpResponse("Some Error, Try Again!")
    
def receive_payment(request):
    
    if (request.method != 'GET'):
        return 
    
    txid  = request.GET.get('txid')
    value = request.GET.get('value')
    status = request.GET.get('status')
    addr = request.GET.get('addr')

    invoice = Invoice.objects.get(address = addr)
    
    invoice.status = int(status)
    if (int(status) == 2):
        invoice.received = value
        invoice.sold = True
        
    invoice.txid = txid
    invoice.save()
    return HttpResponse(200)


#User balance codes
def add_balance(request):
    api_key = 'xDfYvQaaGblBL7kKb4lQ5QRpduF3hHigVBsMhV7Jlyo'
    amount = float(1.00)
    url = 'https://www.blockonomics.co/api/new_address'
    headers = {'Authorization': "Bearer " + api_key}
    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        address = r.json()['address']
        bits = exchanged_rate(amount)
        order_id = uuid.uuid1()
        # Check if the user already has a balance model
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance:
            # If the user has a balance model, use its id
            invoice_id = balance.id
            balance.address = address
            balance.received = 0
            balance.save()
        else:
            # Otherwise, create a new balance model
            invoice = Balance.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8, created_by=request.user)
            invoice_id = invoice.id
        return HttpResponseRedirect(reverse('payment:track_balance', kwargs={'pk': invoice_id}))

    else:
        print(r.status_code, r.text)
        return HttpResponse("Some Error, Try Again!")

def track_balance(request, pk):
    invoice_id = pk
    invoice = Balance.objects.get(id=invoice_id)
    data = {
            'order_id':invoice.order_id,
            'bits':invoice.btcvalue/1e8,
            'value':invoice.balance,
            'addr': invoice.address,
            'status':Balance.STATUS_CHOICES[invoice.status+1][1],
            'invoice_status': invoice.status,
        }
     
    if (invoice.received):
            
        data['paid'] =  invoice.received/1e8
        if (int(invoice.btcvalue) <= int(invoice.received)):
            return redirect('home')
    else:
         data['paid'] = 0  

    return render(request,'invoice.html',context=data)

def receive_balance(request):
    if request.method == 'GET':
        txid = request.GET.get('txid')
        value = float(request.GET.get('value'))
        status = request.GET.get('status')
        addr = request.GET.get('addr')

        invoice = Balance.objects.get(address=addr)
        
        if int(status) == 2:
            invoice.status = int(status)
            invoice.received = value
            invoice.txid = txid
            invoice.balance = 0
            invoice.save()

            # update user's balance
            received = float(invoice.received)
            url = "https://www.blockonomics.co/api/price?currency=USD"
            response = requests.get(url).json()
            usdvalue = received / 1e8 * response["price"]
            invoice.balance += usdvalue
            invoice.save()

        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest()

#Buying
def buy(request,pk):
    product_id = pk
    product = Product.objects.get(id=product_id)
    price = product.price
    balance = Balance.objects.filter(created_by=request.user).first()
    if balance:
        b = balance.balance
        if b is not None:
            remaining = int(price - b)
        else:
            balance.balance = 0
            balance.save()
            remaining = int(price - balance.balance)
        if remaining < 0:
            remaining = 0
    else:
        remaining = price
    if request.method == "POST":
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance:
            b = balance.balance
            check = int(price - b)
            if check > 0:
                return redirect("payment:create_balance")
            else:
                balance.balance = b - price
                balance.save()
                from_email = "Achlogs@achlive.net"

                to_email = request.user.email
                subject = 'Order confirmation'
                text_content = 'Thank you for the order!'
                html_content = render_to_string('email_notify_customer.html', {'order': product.pdf.url},{'product':product})

                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
                product.Status = False
                product.save()
                invoice = Invoice.objects.create(order_id=balance.order_id,
                                address=balance.address,btcvalue=balance.btcvalue, product=product, 
                                created_by=request.user,sold=True,received=balance.received)
                return redirect("account:dashboard")
        else:
            return redirect("payment:create_balance")
    return render(request,'buy.html',context={"price":price,"remain":remaining,"product":product})