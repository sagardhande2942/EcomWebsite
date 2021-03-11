from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact
from math import ceil

def index(request):
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
        'allprods': allprods
    }
    
    return render(request, 'shop/index.html', param)

def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact = Contact(name = name, email = email, phone = phone, desc = desc)
        contact.save()
    return render(request, 'shop/contact.html')

def tracker(request):
    return render(request, 'shop/tracker.html')

def productView(request, myid):
    product = Product.objects.filter(product_id = myid)
    param = {}
    param['prod'] =  product
    return render(request, 'shop/products.html', param)


def checkout(request):
    return HttpResponse("Hii you are in checkout")


def search(request):
    return HttpResponse("Hii you are in search")