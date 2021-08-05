# Generated by Django 3.2.5 on 2021-08-04 16:42

from django.db import migrations
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from accounts.models import User

def create_dummy_data(apps, schema_editor):
    #User = apps.get_model('accounts', 'User')
    User.objects.all().delete()

    employee_title = 'employee'
    customer_title = 'customer'
    default_password = 'test'
    admin_title = 'admin'
    admin_password = 'admin'

    try:
        employee_group = Group.objects.get(name="Employees")
        customer_group = Group.objects.get(name="Customers")
    except:
        employee_group = Group(name="Employees")
        employee_group.save()
        customer_group = Group(name="Customers")
        customer_group.save()

    # Create employee users
    for i in range(20):
        employee_user = User(username=f'{employee_title + str(i)}',
                             password=make_password(default_password),
                             is_employee=1)
        employee_user.save()
        employee_group.user_set.add(employee_user)


    # Create customer users
    for i in range(200):
        customer_user = User(username=f'{customer_title + str(i)}',
                             password=make_password(default_password))
        customer_user.save()
        customer_group.user_set.add(customer_user)

    # Create admin
    admin_user = User(username=admin_title, password=make_password(admin_password), is_superuser=1, is_staff=1)
    admin_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_dummy_data)
    ]