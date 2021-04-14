from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from datetime import date, datetime
# Create your models here.


class ExtendedUser(models.Model):
    cart = models.CharField(default="{}", max_length=1000)
    usr = models.OneToOneField(User, on_delete=CASCADE)
    totcarts = models.CharField(default="{}", max_length=1000, null=True)

class PurchaseDate(models.Model):
    purdate = models.ForeignKey(ExtendedUser, on_delete=CASCADE, default=1, null=True)
    purd = models.DateTimeField(default=datetime.now(), null=True)