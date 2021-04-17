from django.contrib import admin
from .models import Comments, Product, Contact
# Register your models here.

admin.site.register(Product)

admin.site.register(Contact)

admin.site.register(Comments)