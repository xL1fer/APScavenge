#!/bin/sh

pip install django
pip install djangorestframework
pip install python-dotenv
pip install requests
pip install cryptography
pip install psycopg2

python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input

gunicorn approject.wsgi:application --bind 0.0.0.0:8000 --workers=4 --threads=4