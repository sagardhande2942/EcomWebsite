import json
import random
from django.db.models.expressions import Exists
from selenium.webdriver.chrome.options import Options

from stripe.api_resources import product
from accounts.models import ExtendedUser, PurchaseDate, Rating
from django.shortcuts import render
from django.http import HttpResponse
from .models import Comments, Product, Contact, DateCounter, SearchQ, Sellers
from math import ceil, prod
from django.conf import LazySettings, settings 
from django.http.response import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import stripe
import logging
from bs4 import BeautifulSoup
import requests
import simplejson
import threading
import time
import pytz
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium import webdriver
import argparse
import pyperclip as pc
import json
from csv import DictWriter
from uuid import uuid4
from datetime import datetime
import time
import os
import sys
import requests

from datetime import date, datetime, timedelta
logger = logging.getLogger(__name__)

# dateCounter = DateCounter(dateNow=datetime.now(), dateEnd= datetime.now() + timedelta(minutes=1))
# dateCounter.save()
YOUR_DOMAIN = 'http://52.172.129.109/'

price = 0
cart12 = ""
PDFromgetAddtoSuccessPay = PurchaseDate()
daysRequiredInCart = 0

def dailyDeals(a):
    products = Product.objects.all()
    allSubCatList = []
    for i in products:
        if i not in allSubCatList:
            allSubCatList.append(i.subcategory1)
        
    random.shuffle(allSubCatList)
    realSubCats = allSubCatList[0:a]
    allRealProds = []
    for i in realSubCats:
        for j in Product.objects.filter(subcategory1 = i):
            allRealProds.append(j.product_id)

    random.shuffle(allRealProds)
    realRealProds = allRealProds[0:a]
    return realRealProds


def recommended():
    allUsersDict = {}
    allUsers = User.objects.all()
    for i in allUsers:
        allUsersDict[i.id] = dailyDeals(10)
    return allUsersDict


globalDailyDeals = dailyDeals(5)
recommendedItems = recommended()

User = get_user_model()

def countdown():
    global globalDailyDeals
    dateCounter = DateCounter.objects.filter(id = 2) #DateCounter(dateNow=datetime.now(), dateEnd= datetime.now() + timedelta(minutes=1))
    dateCounter.update(dateNow=datetime.now(), dateEnd= datetime.now() + timedelta(minutes=1))
    print('Hii here')
    globalDailyDeals = dailyDeals(5)
    print(globalDailyDeals)
    initiateCountdown()

def initiateCountdown():
    time.sleep(1 * 60)
    print('Hiii')
    countdown()

timer = threading.Thread(target=initiateCountdown)
timer.daemon = True
timer.start() 
threading.Thread.__init__.daemon = True
# initiateCountdown()

@login_required(login_url='/auth/')
def index(request, num):
    global globalDailyDeals
    global recommendedItems
    try:
        recommendedUser = recommendedItems[request.user.id]
    except:
        recommendedItems = recommended()
        recommendedUser = recommendedItems[request.user.id]
    recommendedUser1 = []
    dailyDeals = globalDailyDeals
    dailyDeals1 = []
    for i in dailyDeals:
        dailyDeals1.append(Product.objects.filter(product_id = i))
    for i in recommendedUser:
        recommendedUser1.append(Product.objects.filter(product_id = i))
    dateCounter1 = DateCounter.objects.filter(id = 2)
    # print(dateCounter1)
    try:
        print(dateCounter1[0].dateNow, dateCounter1[0].dateEnd)
    except:
        DateCounter(dateNow=datetime.now(), dateEnd= datetime.now() + timedelta(minutes=1)).save()
        DateCounter(dateNow=datetime.now(), dateEnd= datetime.now() + timedelta(minutes=1)).save()
    #Calling trending product
    if num <= 0:
        num = 1
    if not num:
        num = 1
    maxProduct, maxNum = trendingProduct()
    # print(maxProduct, maxNum)
    maxProductInstance = []
    maxProduct.reverse()
    for i in maxProduct:
        maxProductInstance.append(Product.objects.filter(product_id = int(i[2:])))
    username = request.user.username
    a = ExtendedUser.objects.filter(usr=request.user)
    cart = "{}"
    # print('hiiii This is')
    for i in a:
        # print('THe cart is : ' + i.cart)
        cart = i.cart
    # products = Product.objects.all()
    # print(products)
    # n = len(products)
    # nslides =   n//4 +  ceil(n/4 - n//4)
    allprods = []
    catprods = Product.objects.values('subcategory1', 'product_id')
    cats = {item['subcategory1'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(subcategory1=cat)
        n = len(prod)
        nslides = n//3 + ceil(n/3 - n//3)
        nslides1 = n//5 + ceil(n/5 - n//5)
        nslides2 = n
        allprods.append([prod, range(1, nslides1), nslides1, range(1, nslides), nslides, range(1, nslides2), nslides2])

    # allProds = [
    #     [products, range(1, nslides), nslides],
    #     [products, range(1, nslides), nslides]
    # ]
    random.shuffle(allprods)
    allprodsReal = allprods
    toIncrease = num * 5
    msgToShow  = ""
    if  toIncrease > len(allprods):
        msgToShow = 'You are viewing all products'
    allprods = allprods[0:toIncrease]
    ratingInstance = Product.objects.all()
    ratings = []
    categoriesNeed = []
    for i in ratingInstance:
        ratings.append([i.product_id, max(1, min(5, round(i.rating)))])
    for i in ratingInstance:
        if i.category not in categoriesNeed:
            categoriesNeed.append(i.category)

    subcategoriesDictreal = {}
    for z in categoriesNeed:
        subcategoriesNeed1 = []
        subcategoriesNeed = []
        print(z)
        ratingInstance = Product.objects.filter(category = z)
        for i in ratingInstance:
            # print(i.subcategory)
            if i.subcategory not in subcategoriesNeed:
                subcategoriesNeed.append(i.subcategory)
        
        subcategoriesDict = []
        for i in subcategoriesNeed:
            # print(i)
            aa = Product.objects.filter(subcategory = i)
            for j in aa:
                # print('sub1 : ', j.subcategory1)
                if j.subcategory1 not in subcategoriesNeed1:
                    subcategoriesNeed1.append(j.subcategory1)
            subcategoriesDict.append([i, subcategoriesNeed1])
            subcategoriesNeed1 = []
        subcategoriesDictreal[z] = subcategoriesDict
        subcategoriesDict = []

    # print(subcategoriesDictreal)
    subcategoriesDict5 = subcategoriesDictreal['Electronics']
    subcategoriesDict4 = subcategoriesDictreal['Appliances']
    subcategoriesDict2 = subcategoriesDictreal['Fashion']
    subcategoriesDict1 = subcategoriesDictreal['Grocery']
    subcategoriesDict3 = subcategoriesDictreal['Mobile']
    subcategoriesDict6 = subcategoriesDictreal['Home']
    subcategoriesDict7 = subcategoriesDictreal['Music']
    subcategoriesDict8 = subcategoriesDictreal['Others']
    # subcategoriesDict5= {}
    mostSearch = SearchQ.objects.all()
    mostSearchd = {}
    for i in mostSearch:
        try:
            if mostSearchd[str(i.search)]:
                mostSearchd[str(i.search)] += 1
            else:
                mostSearchd[str(i.search)] = 1
        except Exception as e:
            print(e)
            mostSearchd[str(i.search)] = 1
    # mostSearchd.sort(reverse=True)
    sorted(mostSearchd, reverse=True)
    finalMostSearch = []
    for i in mostSearchd:
        finalMostSearch.append(i)
    finalMostSearch = finalMostSearch[0:5]

    param = {
        'allprods': allprods,
        'items' : len(Product.objects.all()),
        'username': username,
        'cart':cart,
        'trendingProduct':maxProductInstance,
        'trendingNum':maxNum,
        'ratingProduct':ratings,
        'category':categoriesNeed,
        'products': Product.objects.all(),
        'msgToShow':msgToShow,
        'winNo' : num,
        'subcategoriesNeed' : subcategoriesNeed,
        'subcategoriesNeed1' : subcategoriesNeed1,
        'subcategoriesDict1': subcategoriesDict1,
        'subcategoriesDict2': subcategoriesDict2,
        'subcategoriesDict3': subcategoriesDict3,
        'subcategoriesDict4': subcategoriesDict4,
        'subcategoriesDict5': subcategoriesDict5,
        'subcategoriesDict6': subcategoriesDict6,
        'subcategoriesDict7': subcategoriesDict7,
        'subcategoriesDict8': subcategoriesDict8,
        'dateNow': dateCounter1[0].dateNow,
        'dateEnd': dateCounter1[0].dateEnd,
        'dailyDeals':dailyDeals1,
        'recommendedItems': recommendedUser1,
        'mostSearched':finalMostSearch,
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
        # print(cart12)
        return JsonResponse({'hii' : 'bye'})

@login_required(login_url='/auth/')
def create_checkout_session(request):
    if request.method == 'GET':
        # print('Here bois ', request.GET.get('data1', '1'))
        domain_url = 'http://52.172.129.109/'
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
                cancel_url=domain_url + 'shop/cancel/',
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
    # print('Succes pay cart ',c)

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
    # print(b)
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
    global daysRequiredInCart
    currUser = ExtendedUser.objects.filter(usr = request.user)
    # print(currUser[0].cart)
    str1 = currUser[0].cart.split('}')
    res = []
    for i in str1:
        i += '}'
        i = i.replace('{', '[')
        i = i.replace('}', ']')
        res.append(i.strip('][').split(', '))
    print(res)
    try:
        res.remove([''])
    except:
        pass
    zerolen = []
    for i in range(len(res)):
        if len(res[i][0]) == 0:
            zerolen.append(i)
            continue
        res[i] = res[i][0].split(',')
        
        #   print(res[i])
    print(res)
    check123 = False
    for i in res:
        # print('this: ', i)
        if len(i[0]):
            pass
        else:
            # print('hereeeeeee')
            check123 = True
    if check123:
        res.remove([''])  

    diffDict = {}
    for i in range(len(res)):
        diffDict[i] = []
        vb = []
        for j in res[i]:
            j = j.split(',')
            vb.append(j[0].split(':'))
        diffDict[i] = vb
    print(diffDict)
    productIds = []
    try:
        for i in diffDict[0]:
            s1  = i[0]
            s1 = s1[0:-1]
            productIds.append(int(s1[3:]))
    except:
        pass
        
    print(productIds)
    daysRequiredInCart = random.randint(3, 7)
    sellersList = [
        'Ron International', 'Hari Om Shoppie', 'HT-International', 'SimpAlert','OpInChat'
    ]
    xProds = []
    for i in productIds:
        xProds.append(Product.objects.filter(product_id = i))
    allprods = Product.objects.values("product_id", "product_desc", "price", "image", "product_pubs_date", "product_name", 'discount', 'offers')
    username = request.user.username
    p = []
    cnt = 0
    for j in xProds:
        cnt += 1
        # print(i)
        for i in j:
            p.append([i.product_id, i, (i.price + i.price * (i.discount / 100)), daysRequiredInCart, sellersList[random.randint(0,4)]])
    # print(p)
    param = {
        'p' : p,
        'range': range(1, len(Product.objects.all()) + 1),
        'items': len(Product.objects.all()),
        'username':  username,
        'products': xProds,
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
    # print('In Product View')
    username = request.user.username
    cart = ExtendedUser.objects.filter(usr=request.user)
    for i in cart:
        # print(i.cart)
        pass
    product = Product.objects.filter(product_id = myid)
    z = Rating.objects.filter(product_id = myid)
    prodCount = Product.objects.filter(product_id = myid)
    z1 = ""
    offers = Product.objects.filter(product_id = myid)
    if 'T&C' not in offers[0].offers:
        z1 = '''Bank Offer10% off on Axis Bank Debit Cards, up to 1000. On orders of 5000 and aboveT&C
                    Bank Offer5% Unlimited Cashback on Flipkart Axis Bank Credit CardT&C
                    No cost EMI 1,750/month. Standard EMI also availableView Plans
                    View 5 more offers","'''
        offersUse = z1.split('T&C')
    else:
        offersUse = offers[0].offers.split('T&C')
    zz = len(offersUse)
    for i in range(zz):
        if 'Flipkart' in offersUse[i]:
            offersUse[i] = offersUse[i].replace('Flipkart', 'BTB')
    cmtInstance = Comments.objects.filter(product_id = prodCount[0])
    #print(round(product[0].rating))
    param = {
        'incPrice' : round(product[0].price / (1 - product[0].discount / 100), 3),
        'prod': product,
        'username': username,
        'items': len(Product.objects.all()),
        'rating': max(1, min(5, round(product[0].rating))),
        'totReviews':z.count,
        'comments':cmtInstance,
        'totComments':cmtInstance.count,
        'products': Product.objects.all(),
        'offerUse': offersUse,
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
        aReal = a
        a = a.lower()
        # nlp = spacy.load('en_core_web_sm')
        # doc1 = nlp(a.strip())
        # objectsInstance = Product.objects.all()
        # #[id, iphone]
        # productNames  = []
        # for i in objectsInstance:
        #     productNames.append([i.product_id, i.product_name])
        # # df = pd.read_csv('iphones.csv')
        # # print(df)
        # #print (doc1.similarity(nlp('{}'.format(df.loc[1,"name"].value[0]))))
        # #print (doc1.similarity(doc3)) 
        # #print (doc3.similarity(doc4))
        # a =[]
        # b ={}
        # r = []
        # for i in range(len(productNames)):
        #     zx = productNames[i][0]
        #     b[zx] = doc1.similarity(nlp(productNames[i][1].lower()))   
        # #sorted(a, key=float)
        # a1 = list(sorted(b.items(), key=operator.itemgetter(1),reverse=True))
        # d = []
        # for i in a1[0:25]:
        #     d.append(i[0])
        # c = []
        # for i in d:
        #     c.append(Product.objects.filter(product_id = i))
        # print(c[0][0])
        # print(Product.objects.filter(product_id = c[0][0]))


        #MyLogic
        # K = len(a) // 2
        # test_str = a
        # res = [test_str[i: j] for i in range(len(test_str)) for j in range(i + 1, len(test_str) + 1) if len(test_str[i:j]) == K]
        # print('hiii in ssearch')
        # d = Product.objects.all()
        # dd = []
        # b = []
        # for i in d:
        #     dd.append(i)
        # print(res)
        # for a in res:
        # # if not checkx:
        #     iz = 0
        #     for i in dd:
        #         if a in i.product_name.lower():
        #             iz += 1
        #             if iz > 50:
        #                 break
        #             b.append(Product.objects.filter(product_name = i.product_name))

        #     iz = 0
        #     for i in dd:
        #         if a in i.category.lower():
        #             for z in Product.objects.filter(category = i.category):
        #                 iz += 1
        #                 if iz > 50:
        #                     break
        #                 b.append(Product.objects.filter(product_name = z))
        #                 # print(z)
        #             # print('here bois ', Product.objects.filter(category = i.category))

        #     iz = 0
        #     for i in dd:
        #         if a in i.subcategory.lower():
        #             for z in Product.objects.filter(subcategory = i.subcategory):
        #                 iz += 1
        #                 if iz > 50:
        #                     break
        #                 b.append(Product.objects.filter(product_name = z))
        #                 # print(z)
        #             # print('here bois ', Product.objects.filter(subcategory = i.subcategory))
            
        #     iz = 0
        #     for i in dd:
        #         if a in i.subcategory1.lower():
        #             for z in Product.objects.filter(subcategory1 = i.subcategory1):
        #                 iz += 1
        #                 if iz > 50:
        #                     break
        #                 b.append(Product.objects.filter(product_name = z))
        #                 # print(z)
        #             # print('here bois ', Product.objects.filter(subcategory1 = i.subcategory1)) 

        # c = []
        # print('The length is : ', len(b))
        # zzz = []
        # for i in b:
        #     if(i[0].product_name not in zzz):
        #         zzz.append(i[0].product_name)
        # # print(a)
        # for i in zzz:
        #     c.append(Product.objects.filter(product_name = i))

        # if not b: #and not checkx:
        try:
            url="https://www.flipkart.com/search?q="+ aReal.lower() +"&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
            r=requests.get(url)
            soup = BeautifulSoup(r.content, 'html5lib')
            spans=soup.find_all('span',"_10Ermr")
            fl = ''
            k = 0

            for span in spans:
                a = span.text
            #print(a)
            for i in a:
                #print(i)
                if(i == '"'):
                    k = 1
                    continue
                if(k ==1):
                    fl+=i
            productInst = Product.objects.all()
            iz = 0
            #print('this is fl ', fl)
            if not len(fl):
                 raise Exception("Not found any search results")
            a = fl
            d = Product.objects.all()
            dd = []
            b = []
            for i in d:
                dd.append(i)
            for i in dd:
                if a in i.product_name.lower():
                    if len(b)> 50:
                        break
                    b.append(Product.objects.filter(product_id = i.product_id))

            iz = 0
            for i in dd:
                if a in i.category.lower():
                    for z in Product.objects.filter(category = i.category):
                        iz += 1
                        if len(b)> 50:
                            break
                        b.append(Product.objects.filter(product_id = z.product_id))
                        # print(z)
                    # print('here bois ', Product.objects.filter(category = i.category))

            iz = 0
            for i in dd:
                if a in i.subcategory.lower():
                    for z in Product.objects.filter(subcategory = i.subcategory):
                        iz += 1
                        if len(b)> 50:
                            break
                        b.append(Product.objects.filter(product_id = z.product_id))
                        # print(z)
                    # print('here bois ', Product.objects.filter(subcategory = i.subcategory))
            
            iz = 0
            for i in dd:
                if a in i.subcategory1.lower():
                    for z in Product.objects.filter(subcategory1 = i.subcategory1):
                        iz += 1
                        if len(b)> 50:
                            break
                        b.append(Product.objects.filter(product_id = z.product_id))

            if not len(b):
                K = len(a) // 2
                test_str = fl
                res = [test_str[i: j] for i in range(len(test_str)) for j in range(i + 1, len(test_str) + 1) if len(test_str[i:j]) == K]
                #print('hiii in ssearch')
                d = Product.objects.all()
                dd = []
                b = []
                for i in d:
                    dd.append(i)
                #print(res)
        
                for a in res:
                # if not checkx:
                    iz = 0
                    for i in dd:
                        if a in i.product_name.lower():
                            iz += 1
                            if len(b)> 50:
                                break
                            b.append(Product.objects.filter(product_id = i.product_id))

                    iz = 0
                    for i in dd:
                        if a in i.category.lower():
                            for z in Product.objects.filter(category = i.category):
                                iz += 1
                                if len(b)> 50:
                                    break
                                b.append(Product.objects.filter(product_id = z.product_id))
                                # print(z)
                            # print('here bois ', Product.objects.filter(category = i.category))

                    iz = 0
                    for i in dd:
                        if a in i.subcategory.lower():
                            for z in Product.objects.filter(subcategory = i.subcategory):
                                iz += 1
                                if len(b)> 50:
                                    break
                                b.append(Product.objects.filter(product_id = z.product_id))
                                # print(z)
                            # print('here bois ', Product.objects.filter(subcategory = i.subcategory))
                    
                    iz = 0
                    for i in dd:
                        if a in i.subcategory1.lower():
                            for z in Product.objects.filter(subcategory1 = i.subcategory1):
                                iz += 1
                                if len(b)> 50:
                                    break
                                b.append(Product.objects.filter(product_id = z.product_id))

                #print(b)
                if not len(b):
                    return HttpResponse("<h1>Not Found</h1><br><a href='/shop/1'>Home</a>")
                                # print(z)
                            # #print('here bois ', Product.objects.filter(subcategory1 = i.subcategory1)) 

                c = []
                #print(b)
                #print('The length is : ', len(b))
                zzz = []
                for i in b:
                    if(i[0].product_id not in zzz):
                        zzz.append(i[0].product_id)
                # #print(a)
                for i in zzz:
                    c.append(Product.objects.filter(product_id = i))
                SearchQ(search = fl).save()
                return render(request, 'shop/search1.html', {'c':c, 'username' : username, 'value':fl, 'counter' : 1})

                        # #print(z)
            c = []
            #print(b)
            #print('The length is : ', len(b))
            zzz = []
            for i in b:
                #print(i[0].product_id)
                if(i[0].product_id not in zzz):
                    zzz.append(i[0].product_id)
            # #print(a)
            for i in zzz:
                c.append(Product.objects.filter(product_id = i))

                    # #print('here bois ', Product.objects.filter(subcategory1 = i.subcategory1)) 
        except :
            #print('In Except')
            return HttpResponse("<h1>Not Found</h1><br><a href='/shop/1'>Home</a>")
        SearchQ(search = fl).save()
        return render(request, 'shop/search1.html', {'c':c, 'username' : username, 'value':fl, 'counter' : 1})
    return render(request, 'shop/search.html', {'value':'Nothing Found'})

def getLogoutData(request):
    if request.method == "POST":
        #print(request.POST.get('text', 'hii'))
        a = request.POST.get('text', '{}')
        b = ExtendedUser.objects.filter(usr=request.user)
        b.update(cart=a)
        if request.is_ajax():
            vars = {'Hii': 'Sagar', 'Byee' : 'Dhande'}
            json = simplejson.dumps(vars)
        return JsonResponse({"hii":"bye"})


@login_required(login_url='/auth/')
def tracker(request):
    # #print('hiids')  
    username  = request.user.username
    a11 = ExtendedUser.objects.filter(usr=request.user)
    b11 = PurchaseDate.objects.filter(purdate = a11[0])
    for i in a11:
        #print(i)
        pass
    avtime = []
    n10 = 0
    for i in b11:
        avtime.append([i.purd, i.lang, i.lat, i.days, i.state, i.lato, i.lango])
        n10 += 1
    #print(avtime)
    #print(n10, 'is n10')
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
    #print('#printing this', str1)
    if(len(str1) == 2):
        return render(request, 'shop/maps.html')
    #print(str1)
    str1 = str1.split('}')
    res = []
    for i in str1:
        i += '}'
        i = i.replace('{', '[')
        i = i.replace('}', ']')
        res.append(i.strip('][').split(', '))
    # #print(res)
    zerolen = []
    diffDict = {}
    for i in range(len(res)):
        if len(res[i][0]) == 0:
            zerolen.append(i)
            continue
        res[i] = res[i][0].split(',')
        
        #   #print(res[i])
    check = False
    #print(res)
    for i in res:
        #print('this: ', i)
        if len(i[0]):
            pass
        else:
            #print('hereeeeeee')
            check = True
    if check:
        res.remove([''])  
    #print(res) 

    check = False
    #print(res)
    for i in res:
        #print('this: ', i)
        if len(i[0]):
            pass
        else:
            #print('hereeeeeee')
            check = True
    if check:
        res.remove([''])  
    #print(res) 

    for i in range(len(res)):
        diffDict[i] = []
        vb = []
        for j in res[i]:
            j = j.split(',')
            vb.append(j[0].split(':'))
        diffDict[i] = vb

    #print('\nDIff DICT', diffDict)
    finallist = []
    for i in diffDict:
        m = diffDict[i]
        z2 = []
        for j in m:#
            #print(j[0])
            num = ""
            for word in j[0]:
                if word.isdigit():
                    num += word
            #print(num)
            mb = Product.objects.filter(product_id = int(num))
            zxcv = random.randint(0, 7)
            #print(n10 - i - 1)
            if not len(mb):
                continue
            z2.append([mb, j[1], avtime[n10 - i - 1][4], avtime[n10 - i - 1][1], avtime[n10 - i - 1][2], avtime[n10 - i - 1][0], avtime[n10 - i - 1][3] , avtime[n10 - i - 1][6], avtime[n10 - i - 1][5]])
            # assert n10 - i - 1 >= 0
        # n10-=1
        finallist.append(z2)
    #print(finallist)
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
        rating1 = 0
        if not z:
            rating1 = 3
        else:
            rating1 = z[0].rating
        prodInstance = Product.objects.filter(product_id = product_id)
        # print(pytz.all_timezones)
        if not a:
            a = Comments(product_id = prodInstance[0], usr_id = request.user.id, username = request.user.username,
            cmt_title = cmt_title, cmt_desc = cmt_desc, rating = rating1, cmt_time = datetime.now(), edited = False,
            edit_time = datetime.now())
            a.save()
        else:
            a.update(cmt_title = cmt_title, cmt_desc = cmt_desc, rating = z[0].rating, edited = True, edit_time = datetime.now())
    # #print('hiids')  
    username  = request.user.username
    a11 = ExtendedUser.objects.filter(usr=request.user)
    b11 = PurchaseDate.objects.filter(purdate = a11[0])
    for i in a11:
        #print(i)
        pass
    avtime = []
    n10 = 0
    for i in b11:
        avtime.append([i.purd, i.lang, i.lat, i.days, i.state, i.lato, i.lango])
        n10 += 1
    #print(avtime)
    #print(n10, 'is n10')
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
    #print('#printing this', str1)
    if(len(str1) == 2):
        return render(request, 'shop/NoItem.html')
    #print(str1)
    str1 = str1.split('}')
    res = []
    for i in str1:
        i += '}'
        i = i.replace('{', '[')
        i = i.replace('}', ']')
        res.append(i.strip('][').split(', '))
    # #print(res)
    zerolen = []
    diffDict = {}
    for i in range(len(res)):
        if len(res[i][0]) == 0:
            zerolen.append(i)
            continue
        res[i] = res[i][0].split(',')
        
        # #print(res[i])       
    
    check1=  False
    for j in range(1, 5):
        for i in res:
            #print('this: ', i)
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
    #print(diffDict)
    finallist = []
    for i in diffDict:
        m = diffDict[i]
        z2 = []
        for j in m:#
            #print(j[0])
            num = ""
            for word in j[0]:
                if word.isdigit():
                    num += word
            #print(num)
            mb = Product.objects.filter(product_id = int(num))
            z4 = Comments.objects.filter(usr_id = request.user.id, product_id = mb[0])
            try:
                print('This is the comment ', z4[0].cmt_title, ' ', z4[0].cmt_desc)
            except:
                pass
            zxcv = random.randint(0, 7)
            #print(n10 - i - 1)
            if not len(mb):
                continue
            try:
                z2.append([mb, j[1], avtime[n10 - i - 1][4], avtime[n10 - i - 1][1], avtime[n10 - i - 1][2], avtime[n10 - i - 1][0], avtime[n10 - i - 1][3] ,
                avtime[n10 - i - 1][6], avtime[n10 - i - 1][5], z4[0].cmt_title, z4[0].cmt_desc])
            except:
                 z2.append([mb, j[1], avtime[n10 - i - 1][4], avtime[n10 - i - 1][1], avtime[n10 - i - 1][2], avtime[n10 - i - 1][0], avtime[n10 - i - 1][3] ,
                avtime[n10 - i - 1][6], avtime[n10 - i - 1][5], '', ''])
            # assert n10 - i - 1 >= 0
        # n10-=1
        finallist.append(z2)
    useris = ExtendedUser.objects.filter(usr = request.user)
    z3 = Rating.objects.filter(rateusers = useris[0])
    #print(finallist)
    param = {
        'username' : username,
        'final': finallist,
        'res': res,
        'city': states,
        'ratingProduct': Product.objects.all(),
        'ratingUsers':  z3,
        'commentsUsers': z4,
    }
    return render(request, 'shop/trackCart.html', param)

def beforeReload(request):
    #print('IN RELOAD')
    if request.method == "POST":
        a = request.POST.get('text', '{}')
        if(len(a) < 2):
            a = '{}'
        #print(a)
        b = ExtendedUser.objects.filter(usr = request.user)
        b.update(cart = a)
    return JsonResponse({"hii" : "byyw"})

def getAddress(request):
    global PDFromgetAddtoSuccessPay
    global daysRequiredInCart
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
        #print('This is the address : ', a)
        b = json.loads(a)
        # #print(b['lat'])
        c = ExtendedUser.objects.filter(usr = request.user)
        d = datetime.now()
        f = random.randint(0, 7)
        PDFromgetAddtoSuccessPay = PurchaseDate(purdate = c[0], purd = d, state = states[f][0], lato = states[f][2], lango = states[f][1], lat = str(b['lat']), lang = str(b['lon']), days = daysRequiredInCart)
        # PDFromgetAddtoSuccessPay.save()
    return JsonResponse({'hii':'bye'})


def trendingProduct():
    #print('Trending produt start')
    extendedUserInstance = ExtendedUser.objects.all()
    totalObjectsInstance = Product.objects.all()
    # #print(totalObjectsInstance)
    # #print(len(totalObjectsInstance))
    zx= len(totalObjectsInstance)
    finalDictProd = {}
    for i in Product.objects.all():
        zz = Product.objects.filter(product_id = i.product_id)
        # #print(zz)
        # #print(len(zz))
        if not len(zz):
            zx += 1
            continue
        # #print(zz[0].product_id)
        # #print(zz[0].product_name)
        # # zz.update(num = 1)
        # #print(zz[0].rating)
        finalDictProd['pr' + str(i.product_id)] = 0
    for i in extendedUserInstance:
        # #print(i.usr.username)
        totCartsString = i.totcarts
        totCartsArr = totCartsString.split('}')
        for i in range(len(totCartsArr)):
            totCartsArr[i] += '}'
            Stringa = totCartsArr[i]
            if len(Stringa) <= 2:
                continue
            # ##print(Stringa)
            cartToJson = json.loads(Stringa)
            for i in cartToJson:
                try:
                    finalDictProd[i] += cartToJson[i]
                except Exception:
                    continue
                # ##print(finalDictProd[i])
                # ##print(cartToJson[i])
            # #print(finalDictProd)
        # #print(totCartsArr)
    # #print(extendedUserInstance)
    # #print(finalDictProd)
    sorted_values = sorted(finalDictProd.values()) # Sort the values
    sorted_dict = {}

    # #print(sorted_values)
    for i in sorted_values:
        for k in finalDictProd.keys():
            if finalDictProd[k] == i:
                sorted_dict[k] = finalDictProd[k]

    max_ = []
    maxProduct = []
    for i in sorted_dict:
        max_.append([i, sorted_dict[i]])
        maxProduct.append(i)

    # #print(maxProduct, max_)
    #print('Trending produt END')
    return (maxProduct[-5:], max_[-5:])

def rateProduct(request):
    #print('hiih in rateProducxt')
    if request.method == "POST":
        i = request.POST.get('text', '0')
        i = i.split('|')
        uid = ExtendedUser.objects.filter(usr = request.user)
        rateid = Rating.objects.filter(rateusers = uid[0])
        rateid = rateid.filter(product_id = i[0])
        #print(rateid)
        if not rateid:
            saverate = Rating(rateusers = uid[0], product_id = i[0], rating = i[1])
            saverate.save()
        else:
            rateid.update(rating = i[1])
        allRatings = Rating.objects.filter(product_id = i[0])
        ratecnt = 0
        for p in allRatings:
            # #print(p.rating)
            ratecnt += p.rating
        a = Product.objects.filter(product_id = i[0])
        num = a[0].num 
        ratingUpdate = ratecnt / num
        #print('Updated rating for ', a[0].product_name, ' ', ratingUpdate, ' ', i[1], ' ', num)
        a.update(rating = ratecnt / num)  
        return JsonResponse({'hi':'Bye'})


def changeUname(request):
    username = request.user.username
    if request.method == 'POST':
        a = request.POST.get('curuname', '')
        b = request.POST.get('newuname', '')
        c = request.POST.get('curpass', '')
        d = request.POST.get('newpass', '')
        errors = []
        if not c:
            usrInstance = User.objects.all()
            check = False
            for i in usrInstance:
                if a == i.username:
                    if i.username == b:
                        continue
                    check = True
                    z = User.objects.get(username = a)
                    try:
                        z.username = b
                        z.save()
                    except Exception as e:
                        errors.append(e)
                    break
            if not check:
                errors.append('No user with current username found')
            if not len(errors):
                errors.append('Username Succesfully Changed')
                #print(errors)
                return HttpResponse('<h1> DONE </h1><script> window.location.href = "/shop/1";</script>')
            else:
                #print(errors)
                return render(request, 'shop/changeUname.html', {'username' : username, 'errors': errors})
        else:
            usrInstance = User.objects.all()
            check = False
            for i in usrInstance:
                if a == i.username:
                    #print(a)
                    check = True
                    z = User.objects.get(username = a)
                    try:
                        #print(z.password, c)
                        if request.user.check_password(c):
                            z.set_password(d)
                            z.save()
                        else:
                            errors.append('Current Password incorrect')
                    except Exception as e:
                        errors.append(e)
                    break
            if not check:
                errors.append('No user with current username found')
            if not len(errors):
                errors.append('Password Succesfully Changed')
                #print(errors)
                return HttpResponse('<h1> DONE </h1><script> window.location.href = "/shop/1";</script>')
            else:
                #print(errors)
                return render(request, 'shop/changeUname.html', {'username' : a, 'errors': errors})
    return render(request, 'shop/changeUname.html', {'username' : username})



@login_required(login_url='/auth/')
def search1(request, myStr):
    username = request.user.username
    a = myStr
    aReal = a
    a = a.lower()
    d = Product.objects.all()
    dd = []
    for i in d:
        dd.append(i)

    b = []
    # if not checkx:
    for i in dd:
        if a in i.subcategory1.lower():
            for z in Product.objects.filter(subcategory1 = i.subcategory1):
                b.append(Product.objects.filter(product_name = z))
                #print(z)
            #print('here bois ', Product.objects.filter(subcategory1 = i.subcategory1))    
    c = []
    zzz = []
    for i in b:
        if(i[0].product_name not in zzz):
            zzz.append(i[0].product_name)
    #print(a)
    for i in zzz:
        c.append(Product.objects.filter(product_name = i))

    if not b: #and not checkx:
        return HttpResponse("<h1>Not Found</h1><br><a href='/shop/1'>Home</a>")
            
    return render(request, 'shop/search.html', {'c':c, 'username' : username, 'value':aReal})


def sellWithUs(request):
    if request.method == 'POST':
        try:
            # cat = request.POST.get('category', 'Others')
            # sub = request.POST.get('subCategory', 'Other')
            # sub1 = request.POST.get('subCategory1', 'Other1')
            # prod_name = request.POST.get('prodName', 'Asus')
            data1 = request.POST.get('text', '')
            data = data1.split('|')[0]
            print('Data recevied is : ', data)
            category1 = data1.split('|')[1]

            # print('prod name : ', prod_name, 'cat : ', cat, 'sub : ', sub, 'sub1 : ', sub1)

            # args = parser.parse_args()
            ua = UserAgent()
            userAgent = ua.random
            print(userAgent)
            # se = input('Enter What to search\n').strip()
            #prodtype = int(input('Enter product type\n'))
            # file = input("Enter Csv File name\n").strip()
            # df = pd.read_csv('./Csvfiles/'+file+'.csv')
            # c = input("Enter catagory\n").strip()
            # sb = input("Enter SUbcatagory\n").strip()
            # sb1 = input("Enter SUbcatagory1\n").strip()
            # print(len(df))



            # bb = int(input("How Many Products U want(max:25)\n"))
            a=0
            # while(1):
            #     if(bb<=25):            
            #         break
            #     else:
            #         pass
                    # bb = int(input("How Many Products U want(max:25)\n"))
                    
            bb = 1
            # if args.firefox:
            #     profile = webdriver.FirefoxProfile()
            #     profile.set_preference("general.useragent.ovrride", userAgent)    
            #     driver = webdriver.Firefox(firefox_profile=profile, executable_path=r"your gecko driver here")


            # if args.chrome:
            #     from selenium.webdriver.chrome.options import Options
                
                # PROXY = Config["proxy_server"]
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--incognito")
            options.add_argument('window-size=1920x1080')
            #options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 2})
            #options.add_argument('--proxy-server=%s' % PROXY)
            driver= webdriver.Chrome(options=options, executable_path=r"./chromedriver.exe")

            #a = ['Airpod','AirPods are wireless Bluetooth earbuds created by Apple. ... On March 20, 2019, Apple released the 2nd generation AirPods, which feature the H1 chip, longer talk time, and hands-free "Hey Siri" support'
            #     ,'Earphones','Wireless']
            #price1 = 1000

            driver.get("https://flipkart.com")
            driver.find_element_by_xpath('/html/body/div[2]/div/div/button').click()

            se1 = driver.find_element_by_xpath('//*[@id="container"]/div/div[1]/div[1]/div[2]/div[2]/form/div/div/input')

            se1.send_keys(data)

            driver.find_element_by_xpath('//*[@id="container"]/div/div[1]/div[1]/div[2]/div[2]/form/div/button').click()

            time.sleep(3)
            a = 1
            b = 1
            c2 =1
            d2 = 1
            d3 = 1
            #try:
            for i in range(1,2):
                try:
                    prodtype = 1
                    if(prodtype == 1 and i<=4):
                        driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div['+str(i)+']/div/a[2]').click()
                    elif(prodtype == 1 and i>4 and i<=8):
                        
                        driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[3]/div/div['+str(a)+']/div/a[2]').click()
                        a+=1
                    elif(prodtype == 1 and i>8 and i<=12):

                        driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[4]/div/div['+str(b)+']/div/a[2]').click()
                        b+=1
                    elif(prodtype == 1 and i>12 and i<=16):

                        driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[5]/div/div['+str(c2)+']/div/a[2]').click()
                        c2+=1
                    elif(prodtype == 1 and i>16 and i<=20):
                        driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[6]/div/div['+str(d2)+']/div/a[2]').click()
                        d2+=1
                    elif(prodtype == 1 and i>20 and i<=24):
                        driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[7]/div/div['+str(d3)+']/div/a[2]').click()
                        d3+=1
                except:
                    try:
                        prodtype = 2
                        if(prodtype == 2):
                            if(i == 3 or i == 4):
                                continue
                            print('hii')
                            print(i+1)
                            driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div['+str(i+1)+']/div/div/div/a/div[2]/div[1]/div[1]').click()
                    except:
                        prodtype = 3
                        try:
                            if(prodtype == 3 and i<=4):
                                driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[3]/div/div['+str(a)+']/div/div/a[1]').click()
                            if(prodtype == 3 and i>4 and i<=8):
                                print(i)
                                driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[3]/div/div['+str(a)+']/div/div/a[1]').click()
                                a+=1
                            elif(prodtype == 3 and i>8 and i<=12):

                                driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[4]/div/div['+str(b)+']/div/div/a[1]').click()
                                b+=1
                            elif(prodtype == 3 and i>12 and i<=16):

                                driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[5]/div/div['+str(c2)+']/div/div/a[1]').click()
                                c2+=1
                            elif(prodtype == 3 and i>16 and i<=20):
                                driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[6]/div/div['+str(d2)+']/div/div/a[1]').click()
                                d2+=1
                            elif(prodtype == 3 and i>20 and i<=24):
                                driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[7]/div/div['+str(d3)+']/div/div/a[1]').click()
                                d3+=1
                        except:
                            print('Product not found')
                time.sleep(3)
                print("This",prodtype)
                driver.switch_to.window(driver.window_handles[1])
                if(prodtype==3):
                    images = driver.find_elements_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/img')
                    for image in images:
                        img = image.get_attribute('src')
                if(prodtype == 1 or prodtype==2):
                    images = driver.find_elements_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[2]/img')
                    for image in images:
                        img = image.get_attribute('src')
                #print(img)

                name = driver.find_element_by_class_name('B_NuCI').text
                #print(name)
                abb = 0
                strs = ''
                for k in name:
                    if(k == " "):
                        print("hi")
                        name+=k
                        abb+=1
                    strs+=k
                    if(abb == 3):
                        print('dfdfdfdf')
                        break
                print(strs)   
                price = driver.find_element_by_class_name('_25b18c').text
                #price = driver.execute_script('document.getElementsByClassName("_30jeq3 _16Jk6d").value')
                print(price)
                pricee=''
                kk=0
                for g in price:
                    if(g == '₹' or g == '%'):
                        kk+=1
                    if(kk == 1):
                        pricee+=g
                price = price.encode('ascii', 'ignore')
                price = price.decode("utf-8")
                pricee = pricee.encode('ascii', 'ignore')
                pricee = pricee.decode("utf-8") 
                print(price)
                print(pricee)
                print('\u20B9')

                try:
                    kk = 0
                    diss1=''
                    diss = driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div[3]/div[1]/div/div[3]/span').text
                    print("sd1")
                    for di in diss:
                        if(di == '%'):
                            break
                        diss1+=di
                        pass
                except:
                    print("sd")
                    try:
                        diss1=''
                        diss = driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div[4]/div[1]/div/div[3]/span').text
                        for di in diss:
                            if(di == '%'):
                                break
                            diss1+=di
                    except:
                        diss1='30'
                print(diss1)
                        
                try:
                    avail = driver.find_element_by_class_name('_3TT44I').text
                    avail = avail.encode('ascii', 'ignore')
                    avail = avail.decode("utf-8")
                
                except:
                    avail = """Bank Offer10% off on Citi Credit/Debit Cards, up to ₹1750. On orders of ₹4999 and aboveT&Bank Offer5%
                    Unlimited Cashback on Flipkart Axis Bank Credit CardT&Bank OfferFlat ₹75 discount on UPI transaction above ₹10,000
                    in a single cart valueT&CGet a Google Nest Hub (Chalk) at just ₹5,999 on purchase of select TVs laptops, ACs and mobileT&C"""
                    
                #print(avail)
                try:
                    desc = driver.find_element_by_class_name('_2o-xpa').text
                    desc = desc.encode('ascii', 'ignore')
                    desc = desc.decode("utf-8")
                    if(desc == 'NA'):
                        desc = 'Not Available'
                except:
                    desc = 'Not Available'
                print(desc)

                # try:
                #     category1 = driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[1]/div[1]/div/div[1]/a').text
                #  #print(avail)
                # except:
                #     raise 'category not found'
                # print('Category is : ', category1)
                try:
                    # subcat = driver.find_element_by_class_name('_2whKao').innerHtml
                    # subcat = driver.execute_script(
                    #     'document.getElementsByClassName("_2whKao")[0].textContent')
                    subcategory = driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[1]/div[1]/div/div[2]/a').text
                    # subcat = subcat.encode('ascii', 'ignore')
                    # subcat = subcat.decode("utf-8")
                except:
                    raise 'Sub Cat Not Avaliable'
                print('Sub cat is : ',subcategory)

                try:
                    subcategory1 = driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[1]/div[1]/div/div[3]/a').text
                except:
                    raise 'Sub Cat 1 not avaliable'
                print('Sub cat1 is : ', subcategory1)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                data ={
                    "name": strs,
                    "price": pricee,
                    "avail":avail,
                    "desc":desc,
                    "dis":diss1,
                    "image_url":img
                }
                """with open(''+se+'.json', 'a') as outfile:
                    outfile.write(json.dumps(data))
                    outfile.write(",")
                    outfile.close()
                print("productdone",i)
                print("\n\n")"""

                my_dict = {}
                my_dict = data
                print(my_dict)
                # with open('./Csvfiles/'+se+'.csv', 'a') as f:
                #     w = DictWriter(f, my_dict.keys())
                #     if f.tell() == 0:
                #         w.writeheader()
                #         w.writerow(my_dict)
                #     else: 
                #         w.writerow(my_dict)
            # import pandas as pd

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--incognito")
            options.add_argument('window-size=1920x1080')
            #options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 2})
            #options.add_argument('--proxy-server=%s' % PROXY)
            # driver= webdriver.Chrome(options=options, executable_path=r"./chromedriver.exe")

            # driver.get("http://127.0.0.1:8000/admin")
            # email = driver.find_element_by_xpath('//*[@id="id_username"]')
            # passw = driver.find_element_by_xpath('//*[@id="id_password"]')

            # email.send_keys('admin')
            # passw.send_keys('admin')

            # driver.find_element_by_xpath('//*[@id="login-form"]/div[3]/input').click()
            # driver.find_element_by_xpath('//*[@id="content-main"]/div[2]/table/tbody/tr[3]/td[1]/a').click()
            # time.sleep(3)
            try:
                os.mkdir(os.getcwd() + '/shop/images2/'+ category1+'')
            except:
                pass
            for i in range(1):
                cat = category1
                sub_cat = subcategory
                sub_cat1 = subcategory1
                print('Adding product',i)
                print(i)
                config={
                    "name":my_dict['name'],
                    "desc":my_dict['desc'],
                    "price":my_dict['price'],
                    "cat":cat,
                    "sub_cat":sub_cat,
                    "sub_cat1":sub_cat1,
                    "dis":my_dict['dis'],
                    "avail":my_dict['avail'],
                    "image":my_dict['image_url']
                }
                for i in config:
                    print(config[i])
                print("Loading Configurations.....")

                rand_token = uuid4().hex[:8]
                url = config["image"]
                r = requests.get(url, allow_redirects=True)
                open(os.getcwd() + '/shop/images2/' +cat+'/'+cat+''+str(rand_token)+'.png', 'wb').write(r.content)

            #     print('image download done')
            #     name = driver.find_element_by_xpath('//*[@id="id_product_name"]')
            #     name.send_keys(config["name"])
            #     print('Added name Successfully')

            #     prdesc = driver.find_element_by_xpath('//*[@id="id_product_desc"]')
            #     prdesc.send_keys(config["desc"])
            #     print('Added description Successfully')

            #     cat1 = driver.find_element_by_xpath('//*[@id="id_category"]')
            #     cat1.send_keys(config["cat"])
            #     print('Added Categary Successfully')
                
            #     #dis = driver.find_element_by_xpath('//*[@id="id_discount"]')
            #     print(config['dis'])
            #     driver.execute_script('document.getElementById("id_discount").value = '+str(config['dis'])+'')
            #     #dis.send_keys(config["dis"])
            #     print('Added Discount Successfully')

            #     offer = driver.find_element_by_xpath('//*[@id="id_offers"]')
            #     offer.send_keys(config["avail"])
            #     print('Added Offer Successfully')
                
            #     subcat = driver.find_element_by_xpath('//*[@id="id_subcategory"]')
            #     subcat.send_keys(config["sub_cat"])
            #     print("hi",config['dis'])
            #     print('Added SubCategary Successfully')

            #     subcat1 = driver.find_element_by_xpath('//*[@id="id_subcategory1"]')
            #     subcat1.send_keys(config["sub_cat1"])
            #     print('Added SubCat1 Successfully')
                
            #     price = driver.find_element_by_id('id_price')
            #     #price.send_keys(price1)
            #     pri = ''
            #     price1 = config["price"]
            #     #print(price1)
            #     for i in str(price1):
            #         #print(i)
            #         if(i == ','):
            #             continue
            #         pri+=i
            #     print(pri)
            #     driver.execute_script('document.getElementById("id_price").value = '+str(pri)+'')
            #     print('Added price Successfully')

            #     ratingRand = random.randint(1, 5)
            #     driver.execute_script('document.getElementById("id_rating").value = '+str(ratingRand)+'')
                
            #     driver.find_element_by_id("id_image").send_keys(os.getcwd()+"/shop/images2/"+cat+"/"+config["cat"]+""+rand_token+".png")
            #     driver.find_element_by_id("id_image1").send_keys(os.getcwd()+"/shop/images2/"+cat+"/"+config["cat"]+""+rand_token+".png")
            #     print('Added Image Successfully')
            # imageLink = config["cat"]+""+rand_token+".png"
            #     # driver.find_element_by_xpath('//*[@id="product_form"]/div/div/input[2]').click()
            #     #driver.find_element_by_xpath('//*[@id="product_form"]/div/div/input[1]').click()

            #     time.sleep(2)
            #     print('Added Product Successfully')

            driver.quit()
            # print(Product.objects.all()[len(Product.objects.all()) - 1].product_name)
            return JsonResponse({
                    "name":my_dict['name'],
                    "desc":my_dict['desc'],
                    "price":my_dict['price'],
                    "cat":category1,
                    "dis":my_dict['dis'],
                    "avail":my_dict['avail'],
                    "image":my_dict['image_url'],
                    'subcat':subcategory,
                    'subcat1':subcategory1,
                    'rand':rand_token,
                    'error':'',
                })
        except:
            return JsonResponse({'error' : "Sorry there was a error processing your request, try different product"})
        # return render(request, 'shop/prodAdded.html', {'i' : Product.objects.all()[len(Product.objects.all()) - 1]})
    a = Product.objects.all()
    allCat = []
    allSubCat = []
    allSubCat1 = []
    for i in a:
        if i.category not in allCat:
            allCat.append(i.category)
    for i in a:
        if i.subcategory not in allSubCat:
            allSubCat.append(i.subcategory)

    for i in a:
        if i.subcategory1 not in allSubCat1:
            allSubCat1.append(i.subcategory1)

    param = {
        'cat' : allCat,
        'subcat' : allSubCat,
        'subcat1': allSubCat1
    }
        
    return render(request, 'shop/sellWithUs.html', param)
    

def saveProduct(request):
    if request.method == 'POST':
        a = request.POST.get('text', '')
        # print('printing here : ', a)
        my_dict = json.loads(a)
        print(my_dict)
        product_name = my_dict['name']
        product_desc = my_dict['desc']
        price = my_dict['price']
        category1 = my_dict['cat']
        subcategory = my_dict['subcat']
        subcategory1 = my_dict['subcat1']

        ua = UserAgent()
        userAgent = ua.random


        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument('window-size=1920x1080')
        # options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 2})
        # options.add_argument('--proxy-server=%s' % PROXY)
        driver= webdriver.Chrome(options=options, executable_path=r"./chromedriver.exe")

        driver.get("http://127.0.0.1:8000/admin")
        email = driver.find_element_by_xpath('//*[@id="id_username"]')
        passw = driver.find_element_by_xpath('//*[@id="id_password"]')

        email.send_keys('admin')
        passw.send_keys('admin')

        driver.find_element_by_xpath('//*[@id="login-form"]/div[3]/input').click()
        driver.find_element_by_xpath('//*[@id="content-main"]/div[2]/table/tbody/tr[3]/td[1]/a').click()
        time.sleep(3)
        try:
            os.mkdir(os.getcwd() + '/shop/images2/'+ category1+'')
        except:
            pass
        for i in range(1):
            cat = category1
            sub_cat = subcategory
            sub_cat1 = subcategory1
            print('Adding product',i)
            print(i)
            config={
                "name":my_dict['name'],
                "desc":my_dict['desc'],
                "price":my_dict['price'],
                "cat":cat,
                "sub_cat":sub_cat,
                "sub_cat1":sub_cat1,
                "dis":my_dict['dis'],
                "avail":my_dict['avail'],
                "image":my_dict['image']
            }
            for i in config:
                print(config[i])
            print("Loading Configurations.....")

            rand_token = uuid4().hex[:8]
            url = config["image"]
            r = requests.get(url, allow_redirects=True)
            open(os.getcwd() + '/shop/images2/' +cat+'/'+cat+''+str(rand_token)+'.png', 'wb').write(r.content)

            print('image download done')
            name = driver.find_element_by_xpath('//*[@id="id_product_name"]')
            name.send_keys(config["name"])
            print('Added name Successfully')

            prdesc = driver.find_element_by_xpath('//*[@id="id_product_desc"]')
            prdesc.send_keys(config["desc"])
            print('Added description Successfully')

            cat1 = driver.find_element_by_xpath('//*[@id="id_category"]')
            cat1.send_keys(config["cat"])
            print('Added Categary Successfully')
            
            #dis = driver.find_element_by_xpath('//*[@id="id_discount"]')
            print(config['dis'])
            driver.execute_script('document.getElementById("id_discount").value = '+str(config['dis'])+'')
            #dis.send_keys(config["dis"])
            print('Added Discount Successfully')

            offer = driver.find_element_by_xpath('//*[@id="id_offers"]')
            offer.send_keys(config["avail"])
            print('Added Offer Successfully')
            
            subcat = driver.find_element_by_xpath('//*[@id="id_subcategory"]')
            subcat.send_keys(config["sub_cat"])
            print("hi",config['dis'])
            print('Added SubCategary Successfully')

            subcat1 = driver.find_element_by_xpath('//*[@id="id_subcategory1"]')
            subcat1.send_keys(config["sub_cat1"])
            print('Added SubCat1 Successfully')
            
            price = driver.find_element_by_id('id_price')
            #price.send_keys(price1)
            pri = ''
            price1 = config["price"]
            #print(price1)
            for i in str(price1):
                #print(i)
                if(i == ','):
                    continue
                pri+=i
            print(pri)
            driver.execute_script('document.getElementById("id_price").value = '+str(pri)+'')
            print('Added price Successfully')

            ratingRand = random.randint(1, 5)
            driver.execute_script('document.getElementById("id_rating").value = '+str(ratingRand)+'')
            
            driver.find_element_by_id("id_image").send_keys(os.getcwd()+"/shop/images2/"+cat+"/"+config["cat"]+""+rand_token+".png")
            driver.find_element_by_id("id_image1").send_keys(os.getcwd()+"/shop/images2/"+cat+"/"+config["cat"]+""+rand_token+".png")
            print('Added Image Successfully')
            imageLink = config["cat"]+""+rand_token+".png"
            driver.find_element_by_xpath('//*[@id="product_form"]/div/div/input[2]').click()
            #driver.find_element_by_xpath('//*[@id="product_form"]/div/div/input[1]').click()

            time.sleep(2)
            print('Added Product Successfully')

        driver.quit()

        prod = Product.objects.all()[len(Product.objects.all()) - 1]
        usr = request.user.username
        time1 = datetime.now()
        Sellers(user = usr, product_id = prod, time = time1).save()
        for i in Sellers.objects.all():
            print(i.user)
            print(i.product_id)
            print(i.time)
        return JsonResponse({'hii':'bye'})

def sellersList(request):
    b = Sellers.objects.all()
    a = []
    for i in b:
        a.append(i)
    a.reverse()
    return render(request, 'shop/sellersList.html', {'a':a})