# TrashCollectorRepo

## Description
A sample management application for a waste management company. Built in Python and HTML using Django and Bootstrap. Features three layers of access: a customer interface, with options such as scheduling waste pickups and viewing the current account information; an employee interface, which allows for the registration of completed pickups and viewing aggregate data about specific customers and days of pickups; and an administrator interface, that enables the creation and management of all data created within the application. All users have a separate account and login information.

## Installation and Setup Instructions

#### Requirements
Python 3.9
Pipenv 2021.5.29
MySQL
Working internet connection

1. Installation
Download the repository and unzip the file into the directory you want the application to run from.

2. Prerequisite setup
Create a MySQL database. The default for this project is called trash_collector, with a host of 127.0.0.1 and port of 3306. Note the password used to create the database, as this will be necessary for creating the local settings.
These values can be changed as long as the local_settings.py file you create (details below) reflect the changes.
No additional steps are needed for the database, the application will complete the remainder of the setup.

Create a file in the inner trash_collector directory called "local_settings.py".
The structure of this file should be similar to the details provided below in order to run the application properly.

```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = <A SECRET KEY CREATED SPECIFICALLY FOR YOUR APPLICATION>

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django', # default
        'NAME': 'trash_collector', # default
        'USER': <YOUR MYSQL USERNAME>,
        'PASSWORD': <YOUR MYSQL PASSWORD>,
        'HOST': '127.0.0.1', # default value
        'PORT': '3306', # default value
        'OPTIONS': {
            'autocommit': True
        }
    }
}
```
To create a secret key, run these commands in a terminal:
```
pip install django
python3
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key)
```
Copy the created secret key and paste it into the local_settings.py file.


3. Command line setup
Navigate to the repository in a terminal, and run the following commands:

```
pipenv install
pipenv shell
cd trash_collector
python manage.py migrate
python manage.py runserver
```

Note: several of these commands will take some time to fully execute. This is normal, the project is being installed and set up.

Pipenv install and shell will download any required packages to the file directory, and prepare the terminal to run the following commands.
cd trash_collector will navigate to the appropriate directory within the project.
Migrate will configure the database "trash_collector" and implement a sample data set, consisting of 221 accounts, 200 customers, 20 employees, and 1 superuser.
- All employee and customer accounts have a default password of "test".
- Employee accounts have usernames that start with "employee" and end with any number from 0 to 19. (i.e. "employee12")
- Customer accounts have usernames that start with "customer" and end with any number from 0 to 199. (i.e. "customer135")
- The superuser account has a username and password of "admin" by default.
- Note: All names generated in the sample data have been randomly selected, and are not affiliated with or intended to represent any real person, living or dead.
- Note: All addresses and zip codes in the sample data have been randomly selected, and, while the addresses and zip codes are legitimate, are not intended to represent any real persons or places in any capacity beyond the example of the function of this application.
Lastly, runserver will set up the server to run locally, and can be accessed at the location provided in localsettings.py.

## Application Usage
Any time a new terminal is started to run the application, the command ```pipenv shell``` must be run. 
To start the application, run the command ```python manage.py runserver``` from within the outer "trash_collector" folder. This will not open a browser- it only starts the server the application runs from.
To close the application, hold CTRL and press C. This will force the server to stop, but the page will still be displayed in your browser.

To use the application, use a web browser to navigate to either "localhost:8000" or "http://127.0.0.1:8000/".
This will bring you to a login page. From here, you can click "LOG IN" or "SIGN UP". To create a new acount, follow the prompts to create the account and provide any needed information. Note that if the information provided does not reference a real world address, the maps generated on any other pages will not work correctly. Any zip codes outside those used in the data set up may yield no results when using the application search functions later.

If logged in as a customer:
The initial page will display the name of the customer, a navigation bar, and the currently selected weekly pickup day.
From the navigation bar, account details can be viewed, pickup days can be created and changed, and service can be suspended.

If logged in as an employee:
The initial page will display the name of the employee, pickups scheduled for today, a navigation bar, and a map of the customer addresses with pickups today.
From the navigation bar, new pickups can be registered, completed pickups can be viewed and searched, and pickups can be filtered by day. When pickups are filtered by day, click on any of the customer names to see additional information about that customer.