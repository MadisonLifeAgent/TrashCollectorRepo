#############################
###        IMPORTS        ###
#############################
from django.urls import path
from . import views


#############################
###          URLS         ###
#############################
app_name = "employees"
urlpatterns = [
    path('', views.index, name="index"),
    path("create/", views.create, name="create"),
    path("register_pickup/", views.register_pickup, name="register_pickup"),
    path("search_completed_pickups/", views.search_completed_pickups, name="search_completed_pickups"),
    path("customers_by_day/", views.customers_by_day, name="customers_by_day"),
    path("customer_detail/<int:customer_id>/", views.customer_detail, name="customer_detail")
]