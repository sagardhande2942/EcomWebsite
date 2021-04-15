from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from datetime import date, datetime

from django.db.models.fields import NullBooleanField
# Create your models here.


class ExtendedUser(models.Model):
    cart = models.CharField(default="{}", max_length=1000)
    usr = models.OneToOneField(User, on_delete=CASCADE)
    totcarts = models.CharField(default="{}", max_length=1000, null=True)

class PurchaseDate(models.Model):
    purdate = models.ForeignKey(ExtendedUser, on_delete=CASCADE, default=1, null=True)
    purd = models.DateTimeField(default=datetime.now(), null=True)
    state = models.CharField(default='Nagpur', null=True, max_length=50)
    lat = models.CharField(default='21.1015184', null=True, max_length=50)
    lang = models.CharField(default='78.893078', null=True, max_length=50)
    days = models.IntegerField(default='5', null=True)
    lato = models.CharField(default='21.1015184', null=True, max_length=50)
    lango = models.CharField(default='78.893078', null=True, max_length=50)