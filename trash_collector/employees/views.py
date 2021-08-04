from django.http.response import HttpResponseRedirect
from customers.models import Customer, CompletedPickup
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.apps import apps
from .models import Employee
import datetime

# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.


def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers', 'Customer')
    Special_pickups = apps.get_model('customers', 'Special_pickups')

    # Get the current user and the associated employee object
    current_user = request.user
    current_employee = Employee.objects.get(user = current_user)

    todays_customers = get_todays_customers(current_employee)

    context = {
        'user': current_user,
        'todays_customers': todays_customers
    }

    return render(request, 'employees/index.html', context)


def register_pickup(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers', 'Customer')
    CompletedPickup = apps.get_model('customers', 'CompletedPickup')

    # Get the current user and the associated employee object
    current_user = request.user
    current_employee = Employee.objects.get(user = current_user)

    customers = get_todays_customers(current_employee)

    if request.method == "POST":
        # Get selected customers
        selected_customer_ids = request.POST.getlist("customer_checks")
        today = datetime.date.today()

        # Make a new CompletedPickup for each selected customer
        for customer_id in selected_customer_ids:
            current_customer = Customer.objects.get(id=customer_id)
            current_pickup = CompletedPickup(date=today, customer=current_customer, employee=current_employee)
            current_pickup.save()
            # Charges the customer 1 dollar for each pickup, generic value. Could swap for something better later on
            charge_customer(current_customer)

        return HttpResponseRedirect(reverse("employees:index"))
    else:
        eligible_customers = get_eligible_pickup_customers(customers)

        context = {
            "user" : current_user,
            "eligible_customers": eligible_customers
        }
        return render(request, 'employees/register_pickup.html', context)



def search_completed_pickups(request):
    current_user = request.user
    current_employee = Employee.objects.get(user_id=current_user.pk)
    matched_customers = Customer.objects.filter(zipcode=current_employee.zipcode)

    # Search for completed pickup:
    # - Filters:
    # - - Date
    # - - Customer
    if request.method == "POST":
        filter_date = request.POST.get("filter_date")
        filter_customer_id = request.POST.get("filter_customer")
        filter_customer = Customer.objects.get(id=filter_customer_id)
    else:
        filter_date = None
        filter_customer = None
        
    filtered_results = pickup_search_results(current_employee, filter_date, filter_customer)
    context = {
        "search_results": filtered_results,
        "user": current_user,
        "matched_customers": matched_customers
    }
    return render(request, 'employees/search_completed_pickups.html', context)


def customers_by_day(request):
    current_user = request.user
    current_employee = Employee.objects.get(user_id=current_user.pk)
    matched_customers = Customer.objects.filter(zipcode=current_employee.zipcode)
    
    if request.method == "POST":
        filter_date = request.POST.get("filter_date")
    else:
        filter_date = "Monday"

    matched_customers = get_customers_by_pickup_day(current_employee, filter_date)

    context = {
        "user": current_user,
        "matched_customers": matched_customers,
        "selected_day": filter_date
    }

    return render(request, 'employees/customers_by_day.html', context)

def get_customers_by_pickup_day(employee, weekday):
    return Customer.objects.filter(pickup_day=weekday).filter(zipcode=employee.zipcode)


def pickup_search_results(employee, date, customer):
    if date and customer:
        return CompletedPickup.objects.filter(employee_id=employee.pk).filter(date=date).filter(customer_id=customer.pk).order_by('date')
    elif date:
        return CompletedPickup.objects.filter(employee_id=employee.pk).filter(date=date).order_by('date')
    elif customer:
        return CompletedPickup.objects.filter(employee_id=employee.pk).filter(customer_id=customer.pk).order_by('customer_id')
    else:
        return CompletedPickup.objects.filter(employee_id=employee.pk)


def charge_customer(customer):
    customer.balance += 100
    customer.save()

def get_eligible_pickup_customers(todays_customers):
    # Gets all the pickups already completed for today, then compares the customers with a pickup for today and excludes any that overlap
    today = datetime.date.today()
    eligible_pickup_customers = []
    CompletedPickup = apps.get_model('customers', 'CompletedPickup')

    todays_completed_pickups = CompletedPickup.objects.filter(date=today)
    ineligible_ids = [pickup.customer_id for pickup in todays_completed_pickups]

    eligible_pickup_customers = [customer for customer in todays_customers if customer.id not in ineligible_ids]

    return eligible_pickup_customers


def get_todays_customers(current_employee):
    Special_pickups = apps.get_model('customers', 'Special_pickups')
    todays_customers = []

    # Gets the day of the week as an index. 0=Monday, 1=Tuesday, etc.
    today = datetime.date.today()
    weekday = get_weekday_string(today)

    # Retrieve the pickups for the day. Zipcode needs to match employee zip, pickup_day needs to be today, and account needs to be active
    zip_and_day_match_customers = Customer.objects.filter(zipcode = current_employee.zipcode).filter(pickup_day = weekday)
    todays_customers = get_only_active_customers(zip_and_day_match_customers, today)

    # Retrieve the additional special pickups for today, get the customer they belong to, and add to todays_customers
    todays_special_pickups = Special_pickups.objects.filter(special_pickup_date = today)
    special_pickup_customers = []
    for pickup in todays_special_pickups:
        pickup_customer = Customer.objects.filter(id = pickup.customer_id).filter(zipcode = current_employee.zipcode)
        special_pickup_customers.append(pickup_customer)
    active_special_pickup_customers = get_only_active_customers(special_pickup_customers, today)

    # Merge the lists to make sure only unique customers are included
    todays_customers = merge_unique_customers(todays_customers, active_special_pickup_customers)

    return todays_customers

def get_weekday_string(day):
    day_num = day.weekday()

    weekdays = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    return weekdays[day_num]

def get_only_active_customers(customers, today):
    # Get only active accounts, get rid of the rest
    active_customers = []
    for customer in customers:
        suspend_start = customer.suspend_start
        suspend_end = customer.suspend_end
        if (suspend_start and suspend_end) and (not (customer.suspend_start <= today and customer.suspend_end >= today)):
            active_customers.append(customer)
        elif not (suspend_end and suspend_start):
            active_customers.append(customer)

    return active_customers

def merge_unique_customers(customers1, customers2):
    unique_customers = []

    for customer in customers1:
        if customer not in unique_customers:
            unique_customers.append(customer)
    for customer in customers2:
        if customer not in unique_customers:
            unique_customers.append(customer)

    return unique_customers
