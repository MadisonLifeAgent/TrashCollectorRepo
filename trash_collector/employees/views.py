#############################
###        IMPORTS        ###
#############################
from django.http.response import HttpResponseRedirect
from customers.models import Customer, CompletedPickup, Special_pickups
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.apps import apps
from .models import Employee
import datetime


#############################
###         VIEWS         ###
#############################
def index(request):
    # Home page for employees
    Customer = apps.get_model('customers', 'Customer')
    Special_pickups = apps.get_model('customers', 'Special_pickups')

    # Get the current user and the associated employee object
    current_user = request.user

    try:
        current_employee = Employee.objects.get(user = current_user)
    except:
        return create(request)

    todays_customers = get_todays_customers(current_employee)
    
    # Generate a url for the maps API, one pin for each customer
    markers = ""
    for customer in todays_customers:
        current_marker = get_customer_api_address(customer)
        markers = markers + "|" + current_marker

    api_url = "https://maps.googleapis.com/maps/api/staticmap?size=600x600&key=AIzaSyAIYNgoTrCaLJinMQtlC0GtUv8T62RU7Ag&markers=" + markers[1:]

    # Pass context to the HTML page
    context = {
        'user': current_user,
        'todays_customers': todays_customers,
        'current_employee': current_employee,
        "api_url": api_url
    }

    return render(request, 'employees/index.html', context)


def create(request):
    # Employee creation page
    if request.method == "POST":
        name = request.POST.get("name")
        user = request.user
        zipcode = request.POST.get("zipcode")
        if len(zipcode) == 5 and zipcode.isnumeric():
            new_employee = Employee(name=name, user=user, zipcode=zipcode)
            new_employee.save()
            return index(request)
        else:
            return render(request, 'employees/create.html')
    else:
        return render(request, 'employees/create.html')


def register_pickup(request):
    # Page to select pickups to complete
    Customer = apps.get_model('customers', 'Customer')
    CompletedPickup = apps.get_model('customers', 'CompletedPickup')

    # Get the current user and the associated employee object
    current_user = request.user
    current_employee = Employee.objects.get(user = current_user)

    # Retrieve the customers with a pickup today that match zip code and aren't suspended
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
            # Charges the customer 5 dollars for each pickup, generic value. Could swap for something better later on
            charge_customer(current_customer)

        return HttpResponseRedirect(reverse("employees:index"))
    else:
        # Get the customers that have a relevant pickup scheduled for today
        eligible_customers = get_eligible_pickup_customers(customers)

        context = {
            "user" : current_user,
            "eligible_customers": eligible_customers
        }
        return render(request, 'employees/register_pickup.html', context)


def search_completed_pickups(request):
    # Search through completed pickups to verify they have been completed
    current_user = request.user
    current_employee = Employee.objects.get(user_id=current_user.pk)
    matched_customers = Customer.objects.filter(zipcode=current_employee.zipcode)

    # Handle different search queries from page
    if request.method == "POST":
        filter_date = request.POST.get("filter_date")
        filter_customer_id = request.POST.get("filter_customer")
        if filter_customer_id:
            filter_customer = Customer.objects.get(id=filter_customer_id)
        else:
            filter_customer = None
    else:
        filter_date = None
        filter_customer = None
        
    # Generate search results and pass back to page
    filtered_results = pickup_search_results(current_employee, filter_date, filter_customer)
    context = {
        "search_results": filtered_results[0],
        "user": current_user,
        "matched_customers": matched_customers,
        "search_results_string": filtered_results[1],
    }
    return render(request, 'employees/search_completed_pickups.html', context)


def customers_by_day(request):
    # View customers that have a regular pickup scheduled for the provided day of the week
    current_user = request.user
    current_employee = Employee.objects.get(user_id=current_user.pk)
    matched_customers = Customer.objects.filter(zipcode=current_employee.zipcode)

    # Get the filter date from the page. If there isn't one, default to Monday
    filter_date = None
    if request.method == "POST":
        filter_date = request.POST.get("filter_date")
        
    if not filter_date:
        filter_date = "Monday"

    # Generate URL for google API
    matched_customers = get_customers_by_pickup_day(current_employee, filter_date)
    markers = ""
    for customer in matched_customers:
        current_marker = get_customer_api_address(customer)
        markers = markers + "|" + current_marker

    api_url = "https://maps.googleapis.com/maps/api/staticmap?size=600x600&key=AIzaSyAIYNgoTrCaLJinMQtlC0GtUv8T62RU7Ag&markers=" + markers[1:]

    # Pass context to page
    context = {
        "user": current_user,
        "matched_customers": matched_customers,
        "selected_day": filter_date,
        "api_url": api_url
    }

    return render(request, 'employees/customers_by_day.html', context)


def customer_detail(request, customer_id):
    # View customer account information
    customer = Customer.objects.get(id=customer_id)

    # Generate API url to display customer address on map
    customer_api_address = get_customer_api_address(customer)
    api_url = f'https://www.google.com/maps/embed/v1/place?key=AIzaSyAIYNgoTrCaLJinMQtlC0GtUv8T62RU7Ag&q={customer_api_address}'

    additional_pickups = Special_pickups.objects.filter(customer_id=customer)

    # Pass context to page
    context = {
        "customer": customer,
        "api_url": api_url,
        "additional_pickups": additional_pickups
    }

    return render(request, f'employees/customer_detail.html', context)




#############################
###        HELPERS        ###
#############################

def get_customer_api_address(customer):
    # Generate the specific parameter for the customer address to pass to maps API

    # Get data
    customer_raw_address = customer.address
    customer_raw_zipcode = customer.zipcode

    # Process - replace spaces with '+'
    split_address = customer_raw_address.split()
    formatted_address_no_zip = '+'.join(split_address)
    api_address = formatted_address_no_zip + '+' + customer_raw_zipcode

    return api_address


def get_customers_by_pickup_day(employee, weekday):
    # Filter customers to only those that match the employee zipcode and have a matching pickup day
    return Customer.objects.filter(pickup_day=weekday).filter(zipcode=employee.zipcode)


def pickup_search_results(employee, date, customer):
    # Handle search and display string formatting for date and customer searches
    if date and customer:
        filtered_pickups = CompletedPickup.objects.filter(employee_id=employee.pk).filter(date=date).filter(customer_id=customer.pk).order_by('date')
        filtered_pickup_string = f'Search results for {customer.name} on {date}'
    elif date:
        filtered_pickups = CompletedPickup.objects.filter(employee_id=employee.pk).filter(date=date).order_by('date')
        filtered_pickup_string = f'Search results for {date}'
    elif customer:
        filtered_pickups = CompletedPickup.objects.filter(employee_id=employee.pk).filter(customer_id=customer.pk).order_by('customer_id')
        filtered_pickup_string = f'Search results for {customer.name}'
    else:
        filtered_pickups = CompletedPickup.objects.filter(employee_id=employee.pk)
        filtered_pickup_string = 'All pickups'
    return (filtered_pickups, filtered_pickup_string)


def charge_customer(customer):
    # Adds set cost to customer balance
    customer.balance += 5
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
    # Returns all customers that have a matching zip code to the employee, are not suspended, have a weekly pickup that matches today, or have an additional pickup for today
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
        pickup_customer = Customer.objects.filter(id = pickup.customer_id)
        # Need to get the query evaluated before performing an action
        for customer in pickup_customer:
            if customer.zipcode == current_employee.zipcode:
                special_pickup_customers.append(customer)
    active_special_pickup_customers = get_only_active_customers(special_pickup_customers, today)

    # Merge the lists to make sure only unique customers are included
    todays_customers = merge_unique_customers(todays_customers, active_special_pickup_customers)

    return todays_customers


def get_weekday_string(day):
    # Translates weekday index to string
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
    # Compiles two lists of customers without duplication
    unique_customers = []

    for customer in customers1:
        if customer not in unique_customers:
            unique_customers.append(customer)
    for customer in customers2:
        if customer not in unique_customers:
            unique_customers.append(customer)

    return unique_customers
