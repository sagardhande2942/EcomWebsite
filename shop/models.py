from django.db import models
from django.db.models.deletion import CASCADE
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_id = models.AutoField(primary_key=True)
    product_desc = models.CharField(max_length=500)
    product_pubs_date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to="shop/images", default="")
    rating = models.FloatField(default=1, null=True)
    num = models.IntegerField(default=1)
    def __str__(self):
        return self.product_name


class Comments(models.Model):
    product_id = models.ForeignKey(Product, on_delete=CASCADE, null=True, default=1)
    usr_id = models.CharField(default='1', null=True, max_length=50)
    username = models.CharField(default='User', null=True, max_length=50)
    cmt_title = models.CharField(default='Title', null=True, max_length=100)
    cmt_desc = models.CharField(default='This is a demo desc...', null=True, max_length=500)
    rating = models.IntegerField(default=3, null=True)


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    desc = models.CharField(max_length=400)

    def __str__(self):
        return self.name