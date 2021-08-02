from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from .models import Customer

# Create your views here.

# TODO: Create a function for each path created in customers/urls.py. Each will need a template as well.


def index(request):
    # The following line will get the logged-in in user (if there is one) within any view function
    user = request.user
    context = {
        'user': user
    }

    try:
        # This line inside the 'try' will return the customer record of the logged-in user if one exists
        logged_in_customer = Customer.objects.get(user=user)
        context['logged_in_customer'] = logged_in_customer
    except:
        return create(request)

    # It will be necessary while creating a Customer/Employee to assign request.user as the user foreign key

    print(user)
    return render(request, 'customers/index.html', context)

def create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        user = request.user
        zipcode = request.POST.get("zipcode")
        pickup_day = request.POST.get("pickup_day")
        address = request.POST.get("address")
        suspend_start = None
        suspend_end = None
        balance = 0

        new_customer = Customer(name=name, user=user, zipcode=zipcode, pickup_day=pickup_day, address=address, suspend_start=suspend_start, suspend_end=suspend_end, balance=balance)
        new_customer.save()
        return index(request)
    else:
        return render(request, 'customers/create.html')

         
def suspension(request):
    user = request.user
    context = {
        'user': user
    }
    logged_in_customer = Customer.objects.get(user=user)
    context['logged_in_customer'] = logged_in_customer
    if request.method == "POST":
       
        suspend_start = request.POST.get("suspend_start")
        suspend_end = request.POST.get("suspend_end")
        

        logged_in_customer.suspend_start=suspend_start
        logged_in_customer.suspend_end=suspend_end
        logged_in_customer.save()
        return index(request)
    else:
        return render(request, 'customers/suspension.html')