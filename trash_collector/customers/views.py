#############################
###        IMPORTS        ###
#############################
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from .models import Customer, Special_pickups


#############################
###         VIEWS         ###
#############################
def index(request):
    # Basic home page for customer
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

    return render(request, 'customers/index.html', context)


def create(request):
    # Create a new customer
    if request.method == "POST":
        name = request.POST.get("name")
        user = request.user
        zipcode = request.POST.get("zipcode")
        pickup_day = request.POST.get("pickup_day")
        address = request.POST.get("address")
        suspend_start = None
        suspend_end = None
        balance = 0
        if len(zipcode) == 5 and zipcode.isnumeric():
            new_customer = Customer(name=name, user=user, zipcode=zipcode, pickup_day=pickup_day, address=address, suspend_start=suspend_start, suspend_end=suspend_end, balance=balance)
            new_customer.save()
            return index(request)
        else:
            return render(request, 'customers/create.html')
    else:
        return render(request, 'customers/create.html')


def suspension(request):
    # channge or pick suspension dates 
    user = request.user
    context = {
        'user': user
    }
    logged_in_customer = Customer.objects.get(user=user)
    context['logged_in_customer'] = logged_in_customer

    if request.method == "POST":
        suspend_start = request.POST.get("suspend_start")
        suspend_end = request.POST.get("suspend_end")
        # Verify that suspension dates were actually provided
        if suspend_start and suspend_end:
            # Check if suspension dates were given in reverse order
            if suspend_end < suspend_start:
                temp = suspend_end
                suspend_end = suspend_start
                suspend_start = temp

            # Update suspension dates
            logged_in_customer.suspend_start=suspend_start
            logged_in_customer.suspend_end=suspend_end
            logged_in_customer.save()
            return my_account(request)
        else:
            return render(request, 'customers/suspension.html')
    else:
        return render(request, 'customers/suspension.html')


def pickup_day(request):
    # Change regular pickup day
    user = request.user
    context = {
        'user': user
    }

    logged_in_customer = Customer.objects.get(user=user)
    context['logged_in_customer'] = logged_in_customer
    
    # Get pickup day from form
    if request.method == "POST":
        pickup_day = request.POST.get("pickup_day")

        if pickup_day:
            # Saves new user pickup day to database if one was selected
            logged_in_customer.pickup_day=pickup_day
            logged_in_customer.save()

        return my_account(request)

    else:
        return render(request, 'customers/pickup_day.html')


def my_account(request):
    # View customer acount information
    user = request.user
    context = {
        'user': user
    }

    logged_in_customer = Customer.objects.get(user=user)
    context['logged_in_customer'] = logged_in_customer

    # Query special_pickups db and store all values in dictionary for use on myaccount.html in order to list customer's special pickup dates
    all_special_dates = get_all_special_pickup_dates(request)
    context['all_special_dates'] = all_special_dates

    return render(request, 'customers/my_account.html', context)


def special_pickup_date(request):
    # Adds a new additional pickup 
    user = request.user
    context = {
        'user': user
    }

    logged_in_customer = Customer.objects.get(user=user)
    context['logged_in_customer'] = logged_in_customer

    
    if request.method == "POST":
        # Get special pickup date from form
        special_pickup_date = request.POST.get("special_pickup_date")
        customer = logged_in_customer

        if special_pickup_date:
            # Saves new user pickup day to database if a date was selected
            new_special_pickup = Special_pickups(special_pickup_date=special_pickup_date, customer=customer)
            new_special_pickup.save()

        return my_account(request)

    else:
        return render(request, 'customers/specialpickupdate.html')


#############################
###        HELPERS        ###
#############################
def get_all_special_pickup_dates(request):
    # Gets all info from special pickupdates db
    all_special_dates = Special_pickups.objects.all()

    return all_special_dates