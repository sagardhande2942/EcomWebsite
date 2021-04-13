from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
# Create your models here.

class ExtendedUser(models.Model):
    cart = models.CharField(default="{}", max_length=1000)
    usr = models.OneToOneField(User, on_delete=CASCADE)
