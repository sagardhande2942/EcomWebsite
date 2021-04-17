import json
import random

from stripe.api_resources import product
from accounts.models import ExtendedUser, PurchaseDate, Rating
from django.shortcuts import render
from django.http import HttpResponse
from .models import Comments, Product, Contact
from math import ceil, prod
from django.conf import LazySettings, settings 
from django.http.response import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
import stripe
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


YOUR_DOMAIN = 'http://3.143.242.177'

price = 0
cart12 = ""
PDFromgetAddtoSuccessPay = PurchaseDate()

import simplejson
@login_required(login_url='/auth/')
def index(request):
    #Calling trending product
    maxProduct, maxNum = trendingProduct()
    print(maxProduct, maxNum)
    maxProductInstance = Product.objects.filter(product_id = int(maxProduct[2:]))
    username = request.user.username
    a = ExtendedUser.objects.filter(usr=request.user)
    cart = "{}"
    print('hiiii This is')
    for i in a:
        print('THe cart is : ' + i.cart)
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
        nslides = n//2 + ceil(n/2 - n//2)
        nslides1 = n//4 + ceil(n/4 - n//4)
        allprods.append([prod, range(1, nslides1), nslides1, range(1, nslides), nslides])

    # allProds = [
    #     [products, range(1, nslides), nslides],
    #     [products, range(1, nslides), nslides]
    # ]

    ratingInstance = Product.objects.all()
    ratings = []
    categoriesNeed = []
    for i in ratingInstance:
        ratings.append([i.product_id, max(1, min(5, round(i.rating)))])
    for i in ratingInstance:
        if i.category not in categoriesNeed:
            categoriesNeed.append(i.category)
    param = {
        'allprods': allprods,
        'items' : len(Product.objects.all()),
        'username': username,
        'cart':cart,
        'trendingProduct':maxProductInstance,
        'trendingNum':maxNum,
        'ratingProduct':ratings,
        'category':categoriesNeed,
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
        domain_url = 'http://3.143.242.177/'
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
                        'name': 'Your Cart',
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
    global PDFromgetAddtoSuccessPay
    PDFromgetAddtoSuccessPay.save()
    username = request.user.username
    a = ExtendedUser.objects.filter(usr = request.user)

    c = cart12
    print('Succes pay cart ',c)

    a1 = json.loads(c)
    for i in a1:
        zt = Product.objects.filter(product_id = i[2:])
        num = zt[0].num
        zt.update(num = 1 + num)
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
        # if i == len(c) - 1: continue
        b += c[i]
    print(b)
    a.update(totcarts = b, cart = "hiii")
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
    # print(p)
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
    print('In Product View')
    username = request.user.username
    cart = ExtendedUser.objects.filter(usr=request.user)
    for i in cart:
        print(i.cart)
    product = Product.objects.filter(product_id = myid)
    z = Rating.objects.filter(product_id = myid)
    prodCount = Product.objects.filter(product_id = myid)
    cmtInstance = Comments.objects.filter(product_id = prodCount[0])
    print(round(product[0].rating))
    param = {
        'incPrice' : product[0].price + 0.4 * product[0].price,
        'prod': product,
        'username': username,
        'items': len(Product.objects.all()),
        'rating': max(1, min(5, round(product[0].rating))),
        'totReviews':z.count,
        'comments':cmtInstance,
        'totComments':cmtInstance.count,
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
        # if not checkx:
        for i in dd:
            if a in i.product_name.lower():
                b.append(Product.objects.filter(product_name = i.product_name))

        for i in dd:
            if a in i.category.lower():
                for z in Product.objects.filter(category = i.category):
                    b.append(Product.objects.filter(product_name = z))
                    print(z)
                print('here bois ', Product.objects.filter(category = i.category))
        c = []
        zzz = []
        for i in b:
            if(i[0].product_name not in zzz):
                zzz.append(i[0].product_name)
        print(a)
        for i in zzz:
            c.append(Product.objects.filter(product_name = i))

        if not b: #and not checkx:
            return HttpResponse("<h1>Not Found</h1><br><a href='/shop/'>Home</a>")
                
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
    # print('hiids')  
    username  = request.user.username
    a11 = ExtendedUser.objects.filter(usr=request.user)
    b11 = PurchaseDate.objects.filter(purdate = a11[0])
    for i in a11:
        print(i)
    avtime = []
    n10 = 0
    for i in b11:
        avtime.append([i.purd, i.lang, i.lat, i.days, i.state, i.lato, i.lango])
        n10 += 1
    print(avtime)
    print(n10, 'is n10')
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
    check = False
    print(res)
    for i in res:
        print('this: ', i)
        if len(i[0]):
            pass
        else:
            print('hereeeeeee')
            check = True
    if check:
        res.remove([''])  
    print(res) 

    check = False
    print(res)
    for i in res:
        print('this: ', i)
        if len(i[0]):
            pass
        else:
            print('hereeeeeee')
            check = True
    if check:
        res.remove([''])  
    print(res) 

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
            print(n10 - i - 1)
            z2.append([mb, j[1], avtime[n10 - i - 1][4], avtime[n10 - i - 1][1], avtime[n10 - i - 1][2], avtime[n10 - i - 1][0], avtime[n10 - i - 1][3] , avtime[n10 - i - 1][6], avtime[n10 - i - 1][5]])
            # assert n10 - i - 1 >= 0
        # n10-=1
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
    if request.method == 'POST':
        cmt_title = request.POST.get('cmt_title', 'Title')
        cmt_desc = request.POST.get('cmt_desc', 'The is a demo desc')
        product_id = request.POST.get('product_id', '1')
        z1 = Rating.objects.all()
        a = Comments.objects.filter(usr_id = request.user.id, product_id = product_id)
        c = ExtendedUser.objects.filter(usr = request.user)
        z = Rating.objects.filter(rateusers = c[0], product_id = product_id)
        prodInstance = Product.objects.filter(product_id = product_id)
        if not a:
            a = Comments(product_id = prodInstance[0], usr_id = request.user.id, username = request.user.username,
            cmt_title = cmt_title, cmt_desc = cmt_desc, rating = z[0].rating, cmt_time = datetime.now(), edited = False,
            edit_time = datetime.now())
            a.save()
        else:
            a.update(cmt_title = cmt_title, cmt_desc = cmt_desc, rating = z[0].rating, edited = True, edit_time = datetime.now())
    # print('hiids')  
    username  = request.user.username
    a11 = ExtendedUser.objects.filter(usr=request.user)
    b11 = PurchaseDate.objects.filter(purdate = a11[0])
    for i in a11:
        print(i)
    avtime = []
    n10 = 0
    for i in b11:
        avtime.append([i.purd, i.lang, i.lat, i.days, i.state, i.lato, i.lango])
        n10 += 1
    print(avtime)
    print(n10, 'is n10')
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
    check1=  False
    for j in range(1, 5):
        for i in res:
            print('this: ', i)
            if i != ['']:
                check1 = True
                pass
            else:
                check1 = False
                res.remove([''])
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
            print(n10 - i - 1)
            z2.append([mb, j[1], avtime[n10 - i - 1][4], avtime[n10 - i - 1][1], avtime[n10 - i - 1][2], avtime[n10 - i - 1][0], avtime[n10 - i - 1][3] , avtime[n10 - i - 1][6], avtime[n10 - i - 1][5]])
            # assert n10 - i - 1 >= 0
        # n10-=1
        finallist.append(z2)
    useris = ExtendedUser.objects.filter(usr = request.user)
    z3 = Rating.objects.filter(rateusers = useris[0])
    print(finallist)
    param = {
        'username' : username,
        'final': finallist,
        'res': res,
        'city': states,
        'ratingProduct': Product.objects.all(),
        'ratingUsers':  z3,
    }
    return render(request, 'shop/trackCart.html', param)

def beforeReload(request):
    print('IN RELOAD')
    if request.method == "POST":
        a = request.POST.get('text', '{}')
        if(len(a) < 2):
            a = '{}'
        print(a)
        b = ExtendedUser.objects.filter(usr = request.user)
        b.update(cart = a)
    return JsonResponse({"hii" : "byyw"})

def getAddress(request):
    global PDFromgetAddtoSuccessPay
    if request.method == 'POST':
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
        a = request.POST.get('text', "{'lat':18.98, 'lon':72.83}")
        b = json.loads(a)
        # print(b['lat'])
        c = ExtendedUser.objects.filter(usr = request.user)
        d = datetime.now()
        f = random.randint(0, 7)
        PDFromgetAddtoSuccessPay = PurchaseDate(purdate = c[0], purd = d, state = states[f][0], lato = states[f][2], lango = states[f][1], lat = str(b['lat']), lang = str(b['lon']), days = random.randint(3, 7))
        # PDFromgetAddtoSuccessPay.save()
    return JsonResponse({'hii':'bye'})


def trendingProduct():
    print('Trending produt start')
    extendedUserInstance = ExtendedUser.objects.all()
    totalObjectsInstance = Product.objects.all()
    print(len(totalObjectsInstance))
    finalDictProd = {}
    for i in range(1, len(totalObjectsInstance) + 1):
        zz = Product.objects.filter(product_id = i)
        print(zz[0].product_name)
        # zz.update(num = 1)
        print(zz[0].rating)
        finalDictProd['pr' + str(i)] = 0
    for i in extendedUserInstance:
        print(i.usr.username)
        totCartsString = i.totcarts
        totCartsArr = totCartsString.split('}')
        for i in range(len(totCartsArr)):
            totCartsArr[i] += '}'
            Stringa = totCartsArr[i]
            if len(Stringa) <= 2:
                continue
            # print(Stringa)
            cartToJson = json.loads(Stringa)
            for i in cartToJson:
                finalDictProd[i] += cartToJson[i]
            # print(finalDictProd)
        # print(totCartsArr)
    # print(extendedUserInstance)
    max_ = 0
    maxProduct = ""
    for i in finalDictProd:
        if(max_ < finalDictProd[i]):
            max_ = finalDictProd[i]
            maxProduct = i
    print(maxProduct, max_)
    print('Trending produt END')
    return (maxProduct, max_)

def rateProduct(request):
    print('hiih in rateProducxt')
    if request.method == "POST":
        i = request.POST.get('text', '0')
        i = i.split('|')
        uid = ExtendedUser.objects.filter(usr = request.user)
        rateid = Rating.objects.filter(rateusers = uid[0])
        rateid = rateid.filter(product_id = i[0])
        print(rateid)
        if not rateid:
            saverate = Rating(rateusers = uid[0], product_id = i[0], rating = i[1])
            saverate.save()
        else:
            rateid.update(rating = i[1])
        allRatings = Rating.objects.filter(product_id = i[0])
        ratecnt = 0
        for p in allRatings:
            # print(p.rating)
            ratecnt += p.rating
        a = Product.objects.filter(product_id = i[0])
        num = a[0].num 
        ratingUpdate = ratecnt / num
        print('Updated rating for ', a[0].product_name, ' ', ratingUpdate, ' ', i[1], ' ', num)
        a.update(rating = ratecnt / num)  
        return JsonResponse({'hi':'Bye'})

