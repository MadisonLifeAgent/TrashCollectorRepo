#############################
###        IMPORTS        ###
#############################
from django.db import models
from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField


#############################
###        MODELS         ###
#############################
class Customer(models.Model):
    # Base customer class
    name = models.CharField(max_length=50)
    user = models.ForeignKey('accounts.User', blank=True, null=True, on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=5, default='')
    pickup_day = models.CharField(max_length=9, default='Monday')
    address = models.CharField(max_length=50, default='', blank=True)
    suspend_start = models.DateField(null=True, editable=True, blank=True)
    suspend_end = models.DateField(null=True, editable=True, blank=True)
    balance = models.IntegerField(default=0, blank=True)


class CompletedPickup(models.Model):
    # Completed pickups class
    date = models.DateField(null=False, blank=False, editable=False)
    customer = models.ForeignKey('customers.Customer', blank=True, null=False, on_delete=PROTECT)
    employee = models.ForeignKey('employees.Employee', blank=True, null=False, on_delete=PROTECT)


class Special_pickups(models.Model):
    # Special pick up date class
    special_pickup_date = models.DateField(null=False, blank=False, editable=False)
    customer = models.ForeignKey('customers.Customer', blank=True, null=False, on_delete=PROTECT)