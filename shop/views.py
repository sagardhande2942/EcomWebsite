from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact
from math import ceil
from django.conf import settings 
from django.http.response import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
import stripe

YOUR_DOMAIN = 'http://localhost:8000'

price = 0

import simplejson
@login_required(login_url='/auth/')
def index(request):
    username = request.user.username
    # products = Product.objects.all()
    # print(products)
    # n = len(products)
    # nslides =   n//4 +  ceil(n/4 - n//4)
    allprods = []
    catprods = Product.objects.values('category', 'product_id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n//4 + ceil(n/4 - n//4)
        allprods.append([prod, range(1, nslides), nslides])

    # allProds = [
    #     [products, range(1, nslides), nslides],
    #     [products, range(1, nslides), nslides]
    # ]

    param = {
        'allprods': allprods,
        'items' : len(Product.objects.all()),
        'username': username,
    }
    
    return render(request, 'shop/index.html', param)

@csrf_exempt
@login_required(login_url='/auth/')
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@login_required
def getPrice(request):
    global price
    if request.method == 'POST':
        price = int(request.POST.get('text', '1')) * 100
        # print("the data is ", request.POST.get('text', '1'))
        return JsonResponse({'hii' : 'bye'})

@login_required(login_url='/auth/')
def create_checkout_session(request):
    if request.method == 'GET':
        print('Here bois ', request.GET.get('data1', '1'))
        domain_url = 'http://herokudjanogapp.herokuapp.com/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'shop/success/',
                cancel_url=domain_url + 'shop/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': 'Cart',
                        'quantity': 1,
                        'currency': 'inr',
                        'amount': price,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

@login_required(login_url='/auth/')
def successPay(request):
    return render(request, 'shop/success.html')

@login_required(login_url='/auth/')
def cancelPay(request):
    return render(request, 'shop/cancelled.html')

@login_required(login_url='/auth/')
def showCart(request):
    allprods = Product.objects.values("product_id", "product_desc", "price", "image", "product_pubs_date", "product_name")
    p = []
    cnt = 0
    for i in allprods:
        cnt += 1
        p.append([cnt, i])
    print(p)
    param = {
        'p' : p,
        'range': range(1, len(Product.objects.all()) + 1),
        'items': len(Product.objects.all())
    }
    return render(request, 'shop/cart.html', param)

@login_required(login_url='/auth/')
def about(request):
    return render(request, 'shop/about.html')

@login_required(login_url='/auth/')
def checkemailavailability(request, val):
    message = {'result':''}
    if request.is_ajax():
        vars = {'Hii': 'Sagar', 'Byee' : 'Dhande'}
        json = simplejson.dumps(vars)
    return HttpResponse(json, mimetype='application/json')

@login_required(login_url='/auth/')
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact = Contact(name = name, email = email, phone = phone, desc = desc)
        contact.save()
    return render(request, 'shop/contact.html')

@login_required(login_url='/auth/')
def tracker(request):
    return render(request, 'shop/tracker.html')

@login_required(login_url='/auth/')
def productView(request, myid):
    product = Product.objects.filter(product_id = myid)
    param = {}
    param['prod'] =  product
    return render(request, 'shop/products.html', param)

@login_required(login_url='/auth/')
def checkout(request):
    return HttpResponse("Hii you are in checkout")


@login_required(login_url='/auth/')
def search(request):
    return HttpResponse("Hii you are in search")