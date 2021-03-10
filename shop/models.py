from django.db import models
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

    def __str__(self):
        return self.product_name