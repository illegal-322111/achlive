from django.shortcuts import render
from django.http import HttpResponse,HttpResponseBadRequest
from django.conf import settings
from .forms import *
import hmac
from django.views.decorators.csrf import csrf_exempt
import hashlib
from django.http import HttpResponseBadRequest
import requests
import uuid
import json
from store.models import *
from .models import *
import logging
logger = logging.getLogger(__name__)

def create_coinbase_payment(request):
    # Generate a unique payment code or ID for tracking purposes
    payment_code = generate_unique_code()
    user = request.user
    user = Customer.objects.get(user_name=user)
    user_id = user.pk
    # Construct the payload with necessary information
    payload = {
        'name': 'Achlive Pay',
        'description': 'Balance Topup',
        'pricing_type': 'fixed_price',
        "local_price": {
            "amount": "100.00",
            "currency": "USD"
        },
        'metadata': {
            'payment_code': payment_code,
            'customer_id': user_id,
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
    print("Coinbase API Key:", settings.COINBASE_COMMERCE_API_KEY)
    print("Response status code:", response.status_code)
    print("Response text:", response.text)
    print("Response headers:", response.headers)
    print("Response JSON:", response.json())

    # Check if the request was successful
    # Check if the request was successful
    if response.status_code == 201:
        try:
            data = response.json().get('data')
            if data:
                url = data.get('hosted_url')
                address = data.get('web3_data').get('contract_addresses').get('1')  # Assuming you want the Ethereum address
                txid = data.get('code')
                print("Hosted URL:", url)
                print("Ethereum Address:", address)
                print("Transaction ID:", txid)
            else:
                print("No data found in response:", response.text)
                url = None
                address = None
                txid = None
        except Exception as e:
            print("Error parsing JSON response:", e)
            url = None
            address = None
            txid = None


    else:
        print("Error creating payment, status code:", response.status_code)
        url = None
        address = None
        txid = None

    if url:
        bits = exchanged_rate(2000)
        order_id = uuid.uuid1()

        # Check if the user already has a balance model
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance:
            # If the user has a balance model, use its id
            balance.address = address
            balance.txid = txid
            if balance.balance is None:
                balance.balance = 0
            balance.save()
        else:
            # Otherwise, create a new balance model
            invoice = Balance.objects.create(
                order_id=order_id,
                address=address,
                btcvalue=bits * 1e8,
                txid=txid,
                balance=0,
                created_by=request.user
            )

    # Save the payment code and charge object in your database or session for future reference
    return render(request, 'invoice.html', {'addr': address,})

def check_payment_status(customer_id, amount):
    logger.debug('Entering check_payment_status()')
    # Retrieve the payment code and payment ID from your database or session

    try:
        invoice = Balance.objects.get(created_by=customer_id)
        invoice.balance += amount
        invoice.received = 1
        invoice.save()
        username = invoice.created_by.user_name
        email = invoice.created_by.email
        update_user_2(username,email,amount)
        return True
    except Balance.DoesNotExist:
        logger.error('Invoice does not exist')
        return False

def check_payment_status_1(customer_id, amount):
    logger.debug('Entering check_payment_status()')
    # Retrieve the payment code and payment ID from your database or session

    try:
        invoice = Balance.objects.get(created_by=customer_id)
        return True
    except Balance.DoesNotExist:
        logger.error('Invoice does not exist')
        return False

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
        event = payload['event']['data']
        metadata = event.get('metadata', {})
        
        if event_type == 'charge:confirmed':
            customer_id = metadata.get('customer_id')
            amount = float(event['pricing']['local']['amount'])
            if check_payment_status(customer_id, amount):
                
                return HttpResponse(status=202)
            else:
                return HttpResponseBadRequest()

        elif event_type == 'charge:created':
            customer_id = metadata.get('customer_id')
            invoice = Balance.objects.get(created_by=customer_id)
            username = invoice.created_by.user_name
            email = invoice.created_by.email
            return HttpResponse(status=200)
        
        elif event_type == 'charge:failed':
            customer_id = metadata.get('customer_id')
            invoice = Balance.objects.get(created_by=customer_id)
            username = invoice.created_by.user_name
            email = invoice.created_by.email
            amount = float(event['pricing']['local']['amount'])
            update_user_3(username,email,amount)
            return HttpResponse(status=404)

        elif event_type == 'charge:pending':
            customer_id = metadata.get('customer_id')
            invoice = Balance.objects.get(created_by=customer_id)
            username = invoice.created_by.user_name
            email = invoice.created_by.email
            amount = float(event['pricing']['local']['amount'])
            update_user(username,email,amount)
            return HttpResponse(status=200)

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
