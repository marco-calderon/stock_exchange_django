import logging
import os
from datetime import datetime, timedelta
from stock_exchange_django.settings import OER_API_KEY
import django
import requests

# Configure Django for using models outside app.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_exchange_django.settings")
django.setup()


class OpenExchangeRates():
    def __init__(self):
        pass

    def get_today(self):
        r = requests.get('https://openexchangerates.org/api/latest.json?app_id=' + OER_API_KEY)
        return r.json()