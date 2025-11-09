from django.test import TestCase

# Create your tests here.

# mysql -u root -pSsql1591002 "DROP DATABASE IF EXISTS lingq; CREATE DATABASE lingq;"

# Remove-Item -Recurse -Force .\core\migrations; python manage.py makemigrations core; python manage.py migrate ; python manage.py runserver