from django.urls import path

from . import views

# TODO: Determine what distinct pages are required for the customer user stories, add a path for each in urlpatterns

app_name = "customers"
urlpatterns = [
    path('', views.index, name="index"),
    path('create/', views.create, name="create"),
    path('editsuspensiondates/', views.suspension, name="suspension"),
    path('myaccount/', views.my_account, name="my_account"),
    path('changepickupdate/', views.pickup_day, name="pickup_day"),
    path('specialpickup/', views.special_pickup_date, name="special_pickup_date"),
]
