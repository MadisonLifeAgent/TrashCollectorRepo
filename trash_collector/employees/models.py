#############################
###        IMPORTS        ###
#############################
from django.db import models

#############################
###        MODELS         ###
#############################
class Employee(models.Model):
    name = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=5)
    user = models.ForeignKey('accounts.User', blank=True, null=True, on_delete=models.CASCADE)