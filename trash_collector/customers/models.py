from django.db import models
from django.db.models.fields import CharField
# Create your models here.

# TODO: Finish customer model by adding necessary properties to fulfill user stories


class Customer(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey('accounts.User', blank=True, null=True, on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=5, default='')
    pickup_day = models.CharField(max_length=9, default='Monday')
    address = models.CharField(max_length=50, default='', blank=True)
    suspend_start = models.DateField(null=True, editable=True, blank=True)
    suspend_end = models.DateField(null=True, editable=True, blank=True)
    balance = models.IntegerField(default=0, blank=True)
