from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import hmac
import hashlib
import codecs
from django.http import HttpResponseBadRequest
import requests
import uuid
import random
import string
from store.models import *
from .models import *
# Create your views here.
def generate_unique_code():
    # Generate a random alphanumeric code of length 10
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return code
def send_mail(request,product):
    if not request.user.verified:
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
        html_content = render_to_string('email_notify_customer_extraction.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
def exchanged_rate(amount):
    url = "https://www.blockonomics.co/api/price?currency=USD"
    r = requests.get(url)
    response = r.json()
    return amount/response['price']
@login_required
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
            product = invoice.product
            send_mail(request,product)
            if invoice.product.category.name == "Extraction":
                user = request.user
                user.verified = True
                user.save()
            else:
                invoice.product.Status = False
                invoice.product.save()
            return redirect('home')
    else:
        data['paid'] = 0  

    return render(request,'invoice.html',context=data)
@login_required
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
@login_required 
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
@login_required
def add_balance(request):
    api_key = 'ZLHYiSkDEHzZFHHtgWmUvyODD3wA9H67PDgjjzjnFV4'
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
@login_required
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
                return redirect("payment:create_balance")
            else:
                balance.balance = b - price
                balance.save()
                
                send_mail(request,product)
                if product.category.name == "Extraction":
                    user = request.user
                    user.verified = True
                    user.save()
                elif product.category.name == "Clone cards":
                    product.Status = False
                    product.save()
                    return render(request,"cards.html")
                else:
                    product.Status = False
                    product.save()
                invoice = Invoice.objects.create(order_id=balance.order_id,
                                address=balance.address,btcvalue=balance.btcvalue, product=product, 
                                created_by=request.user,sold=True,received=balance.received)
                return redirect("home")
        else:
            return redirect("payment:create_balance")
    return render(request,'buy.html',context={"price":price,"remain":remaining,"product":product})

def cards(request):
    return render(request,"new_home.html")

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_coinbase_payment(request,pk):
    # Generate a unique payment code or ID for tracking purposes
    payment_code = generate_unique_code()
    product = Product.objects.get(id=pk)
    # Construct the payload with necessary information
    payload = {
        'name': 'Achlive Pay',
        'description': f'Payment for {product.name}',
        'pricing_type': 'fixed_price',
        'local_price': {
            'amount': product.price,
            'currency': 'USD'
        },
        'metadata': {
            'payment_code': payment_code
        }
    }

    # Make a POST request to create a new payment
    response = requests.post(
        'https://api.commerce.coinbase.com/charges',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'X-CC-Api-Key': settings.COINBASE_COMMERCE_API_KEY,
            'X-CC-Version': '2018-03-22'
        }
    )

    # Retrieve the charge object from the response
    url = response.json().get('data').get('hosted_url')
    txid = response.json().get('data').get('code')
    if url:
        address = "some address"
        bits = exchanged_rate(product.price)
        order_id = uuid.uuid1()
        invoice = Invoice.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8, product=product,txid=txid, created_by=request.user)
    # Save the payment code and charge object in your database or session for future reference

    return redirect(url)

def check_payment_status(request, payment_id):
    # Retrieve the payment code and payment ID from your database or session

    # Make a GET request to check the payment status
    response = requests.get(
        f'https://api.commerce.coinbase.com/charges/{payment_id}',
        headers={
            'Content-Type': 'application/json',
            'X-CC-Api-Key': settings.COINBASE_COMMERCE_API_KEY,
            'X-CC-Version': '2018-03-22'
        }
    )

    # Retrieve the payment status from the response
    payment_status = response.json().get('data').get('timeline')[0].get('status')

    return HttpResponse("Worked")

import json
from django.http import HttpResponseBadRequest, HttpResponse

def coinbase_webhook(request):
    # Verify the request method
    if request.method != 'POST':
        return HttpResponseBadRequest()

    # Verify the request's content type
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        return HttpResponseBadRequest()

    # Verify the Coinbase Commerce webhook signature
    sig_header = request.headers.get('X-CC-Webhook-Signature')
    payload = json.loads(request.body)
    is_valid_signature = verify_signature(request,payload,sig_header)

    if not is_valid_signature:
        return HttpResponseBadRequest()

    # Process the webhook event
    try:
        payload = json.loads(request.body)
        event_type = payload['event']['type']

        if event_type == 'charge:confirmed':
            return HttpResponse("Worked")
            # Payment confirmed logic
            # Retrieve relevant information from the payload and update your system accordingly
            # For example, you can update the payment status in your database

        elif event_type == 'charge:failed':
            # Payment failed logic
            # Handle the failed payment event
            return HttpResponse("failed")
        elif event_type == 'charge:pending':
            # Payment pending logic
            # Handle the pending payment event
            return HttpResponse("pending")

        # Handle other event types if needed
        else:
            pass

        return HttpResponse(status=200)

    except (KeyError, ValueError) as e:
        # Invalid payload format
        return HttpResponseBadRequest()



def verify_signature(request, payload, sig_header):
    secret = 'a48084b4-859f-4b10-a366-a0c4a3f02f57'  # Replace with your actual webhook secret

    if not all([payload, sig_header, secret]):
        return HttpResponseBadRequest("Missing payload, signature, or secret")

    expected_sig = compute_signature(payload, secret)

    if not secure_compare(expected_sig, sig_header):
        return HttpResponseBadRequest("Signatures do not match")

    # Signature verification successful
    return HttpResponse(status=200)

def compute_signature(payload, secret):
    secret_bytes = codecs.encode(secret, 'utf-8')
    payload_bytes = codecs.encode(payload, 'utf-8')
    signature = hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()
    return signature

def secure_compare(sig1, sig2):
    return hmac.compare_digest(sig1, sig2)

