from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
import requests
import uuid
import random
import string
from store.models import *
from .models import *



# Create your views here.
def exchanged_rate(amount):
    url = "https://www.blockonomics.co/api/price?currency=USD"
    r = requests.get(url)
    response = r.json()
    return amount/response['price']

def generate_unique_code():
    # Generate a random alphanumeric code of length 10
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return code


#Use email functions
def send_mail(request,product):
    if not product.name == "Decryptor":
        from_email = "Achlogs@achlive.net"

        to_email = request.user.email
        subject = 'Order confirmation'
        text_content = 'Thank you for the order!'
        html_content = render_to_string('email_notify_customer.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
    else:
        from_email = "Achlogs@achlive.net"

        to_email = request.user.email
        subject = 'Order confirmation'
        text_content = 'Thank you for the order!'
        html_content = render_to_string('test_email.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

def update_user(username,email,amount):
        from_email = "Achlogs@achlive.net"
        username = username
        to_email = email
        subject = 'Charge Pending'
        text_content = 'Transaction Pending'
        html_content = render_to_string('balance_notify_customer.html',{'amount':amount,'user':username})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        
def update_user_2(username,email,amount):
    from_email = "Achlogs@achlive.net"
    to_email = email
    subject = 'Balance Updated'
    text_content = 'Transaction successful'
    html_content = render_to_string('balance_notify_customer2.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def update_user_1(username,email,amount):
    from_email = "Achlogs@achlive.net"
    to_email = email
    subject = 'Balance Updated'
    text_content = 'Transaction successful'
    html_content = render_to_string('balance_notify_customer1.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    
def update_user_3(username,email,amount):
    from_email = "Achlogs@achlive.net"
    to_email = email
    subject = 'Charge Failed'
    text_content = 'Transaction failed'
    html_content = render_to_string('balance_notify_customer3.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def cards_mail(request):
    from_email = "Achlogs@achlive.net"

    to_email = request.user.email
    subject = 'Order confirmation'
    text_content = 'Thank you for the order!'
    html_content = render_to_string('cards_notify.html')

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    return redirect('home')

#Buying
@login_required
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
                return redirect("payment:coinbase")
            else:
                balance.balance = b - price
                balance.save()
                
                
                if product.category.name == "Extraction":
                    user = request.user
                    user.verified = True
                    user.save()
                    send_mail(request,product)
                elif product.category.name == "Clone cards":
                    product.Status = False
                    product.save()
                    return render(request,"cards.html")
                else:
                    product.Status = False
                    product.save()
                    send_mail(request,product)
                invoice = Invoice.objects.create(order_id=balance.order_id,
                                address=balance.address,btcvalue=balance.btcvalue, product=product, 
                                created_by=request.user,sold=True,received=balance.received)
                return redirect("home")
        else:
            return redirect("payment:coinbase")
    return render(request,'buy.html',context={"price":price,"remain":remaining,"product":product})

def cards(request):
    return render(request,"new_home.html")


#Adding balance
@login_required
def add_balance(request):
    api_key = 'f2qchMQe1X3MaEaGNyK5qr1p1vJRCzetaXZ7gylpVS0'
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
            if balance.balance is None:
                balance.balance = 0
                balance.save()
            
        else:
            # Otherwise, create a new balance model
            invoice = Balance.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8, created_by=request.user, balance=0)
            invoice_id = invoice.id
        return HttpResponseRedirect(reverse('payment:track_balance', kwargs={'pk': invoice_id}))

    else:
        print(r.status_code, r.text)
        return HttpResponse(f"Some Error, Try Again! {r.status_code}")
@login_required
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
        try:
            invoice = Balance.objects.get(address=addr)
        except Balance.DoesNotExist:
            update_user_3(request.user.user_name,request.user.email,value)
            return HttpResponse(status=200)
        if int(status) == 0:
            update_user_1(request.user.user_name,request.user.email,value)
        elif int(status) == 1:
            update_user(request.user.user_name,request.user.email,value)
        elif int(status) == 2:
            invoice.status = int(status)
            invoice.received = value
            invoice.txid = txid
            invoice.save()
            # update user's balance
            received = float(invoice.received)
            url = "https://www.blockonomics.co/api/price?currency=USD"
            response = requests.get(url).json()
            usdvalue = received / 1e8 * response["price"]
            invoice.balance += usdvalue
            invoice.save()
            update_user_2(request.user.user_name,request.user.email,usdvalue)

        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest()

def send_mail_kelly(request):
    if request.method == "POST":
        Form = EmailForms(request.POST)
        if Form.is_valid():
            from_email = "Achlogs@achlive.net"

            to_email = Form.cleaned_data["email"]
            subject = 'Order compromised'
            text_content = 'Your order has been compromised'
            html_content = render_to_string('test_email.html')

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            return HttpResponse("Message Sent")
    else:
        Form = EmailForms()
    return render(request, "email.html", {"form": Form})