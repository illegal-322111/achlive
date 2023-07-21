from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseBadRequest,JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import hmac
from django.views.decorators.csrf import csrf_exempt
import hashlib
from django.http import HttpResponseBadRequest
import requests
import uuid
import random
import string
import json
from store.models import *
from .models import *
import logging
logger = logging.getLogger(__name__)
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
        html_content = render_to_string('email_notify_customer_extraction.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

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
            return redirect("payment:coinbase")
    return render(request,'buy.html',context={"price":price,"remain":remaining,"product":product})

def cards(request):
    return render(request,"new_home.html")



@csrf_exempt
@login_required
def create_coinbase_payment(request):
    # Generate a unique payment code or ID for tracking purposes
    payment_code = generate_unique_code()

    # Construct the payload with necessary information
    payload = {
        'name': 'Achlive Pay',
        'description': 'Balance Topup',
        'pricing_type': 'no_price',
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
        address = 'some address'
        bits = exchanged_rate(2000)
        order_id = uuid.uuid1()
        # Check if the user already has a balance model
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance:
            # If the user has a balance model, use its id
            balance.address = address
            balance.received = 0
            balance.save()
        else:
            # Otherwise, create a new balance model
            invoice = Balance.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8,txid=txid, created_by=request.user)
    # Save the payment code and charge object in your database or session for future reference

    return redirect(url)



def check_payment_status(payment_code, amount):
    logger.debug('Entering check_payment_status()')
    # Retrieve the payment code and payment ID from your database or session

    try:
        invoice = Balance.objects.get(txid=payment_code)
        invoice.balance += amount
        invoice.save()
        logger.debug('Updated invoice successfully')
        return redirect('home')
    except Invoice.DoesNotExist:
        logger.error('Invoice does not exist')
        return HttpResponse("Something went wrong contact chat support")




@csrf_exempt
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
    payload = request.body
    is_valid_signature = verify_signature(payload, sig_header)

    if not is_valid_signature:
        return HttpResponseBadRequest()

    # Verify the Referer header
    

    # Process the webhook event
    try:
        payload = json.loads(request.body)
        event_type = payload['event']['type']

        if event_type == 'charge:confirmed':
            # Payment confirmed logic
            # Retrieve relevant information from the payload and update your system accordingly
            # For example, you can update the payment status in your database
            payment_code = payload['event']['data']['code']
            amount = payload['event']['data']['amount']
            logger.debug('Entering check_payment_status()')
            #check_payment_status(payment_code, amount)
            return JsonResponse(payment_code)

            

        elif event_type == 'charge:failed':
            # Payment failed logic
            # Handle the failed payment event
            return HttpResponse("Payment Failed")

        elif event_type == 'charge:pending':
            # Payment pending logic
            # Handle the pending payment event
            return HttpResponse("pending")

        # Handle other event types if needed

        return HttpResponse(status=200)

    except (KeyError, ValueError) as e:
        # Invalid payload format
        return HttpResponseBadRequest()


def verify_signature(payload, sig_header):
    secret = 'a48084b4-859f-4b10-a366-a0c4a3f02f57'  # Replace with your actual webhook secret

    if not all([payload, sig_header, secret]):
        return False

    expected_sig = compute_signature(payload, secret)

    if not secure_compare(expected_sig, sig_header):
        return False

    # Signature verification successful
    return True


def compute_signature(payload, secret):
    secret_bytes = bytes(secret, 'utf-8')
    signature = hmac.new(secret_bytes, payload, hashlib.sha256).hexdigest()
    return signature


def secure_compare(sig1, sig2):
    return hmac.compare_digest(sig1, sig2)
