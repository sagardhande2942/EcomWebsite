from os import truncate
from django.db import models
from django.db.models.deletion import CASCADE
from datetime import datetime
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_id = models.AutoField(primary_key=True)
    product_desc = models.CharField(max_length=500)
    product_pubs_date = models.DateField(auto_now=True)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    discount = models.IntegerField(default=30)
    offers = models.CharField(max_length=500, default="")
    subcategory1 = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to="shop/images", default="")
    image1 = models.ImageField(upload_to="shop/images1", default="")
    rating = models.FloatField(default=1, null=True)
    num = models.IntegerField(default=1)
    seller = models.CharField(default='BTB', null=True, max_length=300, blank=True)
    def __str__(self):
        return self.product_name


class Comments(models.Model):
    product_id = models.ForeignKey(Product, on_delete=CASCADE, null=True, default=1)
    usr_id = models.CharField(default='1', null=True, max_length=50)
    username = models.CharField(default='User', null=True, max_length=50)
    cmt_title = models.CharField(default='Title', null=True, max_length=100)
    cmt_desc = models.CharField(default='This is a demo desc...', null=True, max_length=500)
    rating = models.IntegerField(default=3, null=True)
    edited = models.BooleanField(default=False)
    edit_time = models.DateTimeField(default = datetime.now())
    cmt_time = models.DateTimeField(default=datetime.now())


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    desc = models.CharField(max_length=400)

    def __str__(self):
        return self.name


class DateCounter(models.Model):
    dateNow = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    dateEnd = models.DateTimeField(auto_now_add=False, blank=True, null=True)

class SearchQ(models.Model):
    search = models.CharField(max_length=100, blank=True, default='')


class Sellers(models.Model):
    user = models.CharField(default='1', null=True, blank=True, max_length=200)
    product_id = models.ForeignKey(Product, on_delete=CASCADE, null=True, default=1)
    time = models.DateTimeField(auto_now_add=False)

