import random
from accounts.models import ExtendedUser, PurchaseDate
from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact
from math import ceil, prod
from django.conf import settings 
from django.http.response import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
import stripe
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


YOUR_DOMAIN = 'http://localhost:8000'

price = 0
cart12 = ""

import simplejson
@login_required(login_url='/auth/')
def index(request):
    username = request.user.username
    a = ExtendedUser.objects.filter(usr=request.user)
    cart = ""
    for i in a:
        cart = i.cart
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
        'cart':cart,
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

@login_required
def getCart(request):
    global cart12
    if request.method == "POST":
        cart12 = request.POST.get('text', '{}')
        print(cart12)
        return JsonResponse({'hii' : 'bye'})

@login_required(login_url='/auth/')
def create_checkout_session(request):
    if request.method == 'GET':
        print('Here bois ', request.GET.get('data1', '1'))
        domain_url = 'http://127.0.0.1:8000/'
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
    global cart12
    username = request.user.username
    a = ExtendedUser.objects.filter(usr = request.user)
    d = datetime.now()
    e = PurchaseDate(purdate = a[0], purd = d)
    e.save()
    c = cart12
    for i in a:
        c += i.totcarts
    b = ""
    for i in range(len(c)):
        if c[i] == '{':
            if i + 1 < len(c) and  c[i + 1] == '}':
                i += 2
                continue
        if(c[i] == '{'):
            if i + 1 < len(c) and  c[i + 1] == '{':
                continue
        if(c[i] == '}'):
            if(i + 1 < len(c) and c[i + 1] == '}'):
                continue
        if i == len(c) - 1: continue
        b += c[i]
    print(b)
    a.update(totcarts = b, cart = "{}")
    context = {
        'username' : username
    }
    return render(request, 'shop/success.html', context)

@login_required(login_url='/auth/')
def cancelPay(request):
    username = request.user.username
    context = {
        'username' : username
    }
    return render(request, 'shop/cancelled.html', context)

@login_required(login_url='/auth/')
def showCart(request):
    allprods = Product.objects.values("product_id", "product_desc", "price", "image", "product_pubs_date", "product_name")
    username = request.user.username
    p = []
    cnt = 0
    for i in allprods:
        cnt += 1
        p.append([cnt, i])
    print(p)
    param = {
        'p' : p,
        'range': range(1, len(Product.objects.all()) + 1),
        'items': len(Product.objects.all()),
        'username':  username
    }
    return render(request, 'shop/cart.html', param)

@login_required(login_url='/auth/')
def about(request):
    username = request.user.username
    context = {
        'username' : username
    }
    return render(request, 'shop/about.html', context)

@login_required(login_url='/auth/')
def checkemailavailability(request, val):
    message = {'result':''}
    if request.is_ajax():
        vars = {'Hii': 'Sagar', 'Byee' : 'Dhande'}
        json = simplejson.dumps(vars)
    return HttpResponse(json, mimetype='application/json')

@login_required(login_url='/auth/')
def contact(request):
    username = request.user.username
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact = Contact(name = name, email = email, phone = phone, desc = desc)
        contact.save()
    context = {
        'username' : username
    }
    return render(request, 'shop/contact.html', context)


@login_required(login_url='/auth/')
def productView(request, myid):
    username = request.user.username
    cart = ExtendedUser.objects.filter(usr=request.user)
    for i in cart:
        print(i.cart)
    product = Product.objects.filter(product_id = myid)
    param = {
        'prod': product,
        'username': username,
        'items': len(Product.objects.all()),
    }
    return render(request, 'shop/products.html', param)

@login_required(login_url='/auth/')
def checkout(request):
    return HttpResponse("Hii you are in checkout")


@login_required(login_url='/auth/')
def search(request):
    username = request.user.username
    if request.method == "POST":
        a = request.POST.get('search','no')
        a = a.lower()
        d = Product.objects.all()
        dd = []
        for i in d:
            dd.append(i)

        b = []
        for i in dd:
            if a in i.product_name.lower():
                b.append(Product.objects.filter(product_name = i))
                       
        c = []
        if not b:
            return HttpResponse("<h1>Not Found</h1><br><a href='/shop/'>Home</a>")
        print(a)
        for i in b:
            c.append(i)
        return render(request, 'shop/search.html', {'c':c, 'username' : username})
    return render(request, 'shop/search.html', {'value':'Nothing Found'})

def getLogoutData(request):
    if request.method == "POST":
        print(request.POST.get('text', 'hii'))
        a = request.POST.get('text', '{}')
        b = ExtendedUser.objects.filter(usr=request.user)
        b.update(cart=a)
        if request.is_ajax():
            vars = {'Hii': 'Sagar', 'Byee' : 'Dhande'}
            json = simplejson.dumps(vars)
        return JsonResponse({"hii":"bye"})


@login_required(login_url='/auth/')
def tracker(request):
    print('hiids')  
    username  = request.user.username
    a11 = ExtendedUser.objects.filter(usr=request.user)
    b11 = PurchaseDate.objects.filter(purdate = a11[0])
    avtime = []
    n10 = 0
    for i in b11:
        avtime.append(i.purd)
        n10 += 1
    states = [
        ['Nagpur', 78.893078, 21.1015184],
        ['Nashik', 73.90984434482529, 19.890527214221166],
        ['Pune', 73.7191995481777, 18.575145787488346],
        ['Surat', 72.95662036158728, 21.113012603007366],
        ['Ahemdabad', 73.02994528337483, 22.55593501134834],
        ['Kolhapur',  73.85723039994883, 16.98177500464568,],
        ['Nanded', 76.88549827649183, 19.12996201223232],
        ['Navi Mumbai', 73.14423088426301, 18.68300231807807]
    ]

    z = ExtendedUser.objects.filter(usr = request.user)
    a = []
    b = []
    str1 = z[0].totcarts
    print('printing this', str1)
    if(len(str1) == 2):
        return render(request, 'shop/NoItem.html')
    print(str1)
    str1 = str1.split('}')
    res = []
    for i in str1:
        i += '}'
        i = i.replace('{', '[')
        i = i.replace('}', ']')
        res.append(i.strip('][').split(', '))
    # print(res)
    zerolen = []
    diffDict = {}
    for i in range(len(res)):
        if len(res[i][0]) == 0:
            zerolen.append(i)
            continue
        res[i] = res[i][0].split(',')
        
        #   print(res[i])
    
    # res.remove([''])   
    for i in range(len(res)):
        diffDict[i] = []
        vb = []
        for j in res[i]:
            j = j.split(',')
            vb.append(j[0].split(':'))
        diffDict[i] = vb
    print(diffDict)
    finallist = []
    for i in diffDict:
        m = diffDict[i]
        z2 = []
        for j in m:#
            print(j[0])
            num = ""
            for word in j[0]:
                if word.isdigit():
                    num += word
            print(num)
            mb = Product.objects.filter(product_id = int(num))
            zxcv = random.randint(0, 7)
            z2.append([mb, j[1], random.randint(3, 7),  states[zxcv][0], states[zxcv][2], states[zxcv][1], avtime[n10 - i - 1]])
        finallist.append(z2)
    print(finallist)
    param = {
        'username' : username,
        'final': finallist,
        'res': res,
        'city': states,
    }
    return render(request, 'shop/maps.html', param)


@login_required(login_url='/auth/')
def trackCart(request):
    print('hiids')  
    username  = request.user.username
    a11 = ExtendedUser.objects.filter(usr=request.user)
    b11 = PurchaseDate.objects.filter(purdate = a11[0])
    avtime = []
    n10 = 0
    for i in b11:
        avtime.append(i.purd)
        n10 += 1
    states = [
        ['Nagpur', 78.893078, 21.1015184],
        ['Nashik', 73.90984434482529, 19.890527214221166],
        ['Pune', 73.7191995481777, 18.575145787488346],
        ['Surat', 72.95662036158728, 21.113012603007366],
        ['Ahemdabad', 73.02994528337483, 22.55593501134834],
        ['Kolhapur',  73.85723039994883, 16.98177500464568,],
        ['Nanded', 76.88549827649183, 19.12996201223232],
        ['Navi Mumbai', 73.14423088426301, 18.68300231807807]
    ]

    z = ExtendedUser.objects.filter(usr = request.user)
    a = []
    b = []
    str1 = z[0].totcarts
    print('printing this', str1)
    if(len(str1) == 2):
        return render(request, 'shop/NoItem.html')
    print(str1)
    str1 = str1.split('}')
    res = []
    for i in str1:
        i += '}'
        i = i.replace('{', '[')
        i = i.replace('}', ']')
        res.append(i.strip('][').split(', '))
    # print(res)
    zerolen = []
    diffDict = {}
    for i in range(len(res)):
        if len(res[i][0]) == 0:
            zerolen.append(i)
            continue
        res[i] = res[i][0].split(',')
        
        #   print(res[i])
    
    # res.remove([''])   
    for i in range(len(res)):
        diffDict[i] = []
        vb = []
        for j in res[i]:
            j = j.split(',')
            vb.append(j[0].split(':'))
        diffDict[i] = vb
    print(diffDict)
    finallist = []
    for i in diffDict:
        m = diffDict[i]
        z2 = []
        for j in m:#
            print(j[0])
            num = ""
            for word in j[0]:
                if word.isdigit():
                    num += word
            print(num)
            mb = Product.objects.filter(product_id = int(num))
            zxcv = random.randint(0, 7)
            z2.append([mb, j[1], random.randint(3, 7),  states[zxcv][0], states[zxcv][2], states[zxcv][1], avtime[n10 - i - 1]])
        finallist.append(z2)
    print(finallist)
    param = {
        'username' : username,
        'final': finallist,
        'res': res,
        'city': states,
    }
    return render(request, 'shop/trackCart.html', param)