import threading
import environ
from open_exchange_rates import OpenExchangeRates
from .models import Record
from datetime import datetime, timedelta
from django.http import JsonResponse
from decimal import *

def keep_awake(request):
    return JsonResponse({ 'message': 'OK', 'ok': True })

class ScrapBackgroundTask(threading.Thread):
    def run(self,*args,**kwargs):
        while True:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(hours=23, minutes=59)

            api = OpenExchangeRates()
            data = api.get_today()

            start_date = start_date - timedelta(days=1)
            end_date = start_date + timedelta(days=1)
            prev_rate = 0.0
            difference = 0.0
            prev_record = None

            if data['rates']:
                codes = list(data['rates'].keys())
                for code in codes:
                    try:
                        # Gets the previous entry
                        prev_record = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code))[0]
                    except Exception:
                        pass
                        
                    r = Record()
                    r.date = datetime.now()
                    r.currency_code = code,
                    r.rate = float(data['rates'][code])
                    if prev_record is not None:
                        # Set if found
                        prev_rate = prev_record.rate
                        difference = Decimal(r.rate) - Decimal(prev_record.rate)
                        r.prev_rate = prev_rate
                        r.difference = difference
                    r.save()


def scrap(request):
    env = environ.Env()
    secret = env('TOKEN')
    if ('key' in request.GET and request.GET['key'] == secret):
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(hours=23, minutes=59)

        # Avoid adding duplicated objects if it exists.
        results = Record.objects.filter(date__gte=start_date, date__lte=end_date).first()
        if results is not None:
            return JsonResponse({ 'message': 'Already added for today', 'ok': False })
        
        # Execute async task for scrapping and storing into database
        t = ScrapBackgroundTask()
        t.start()

        return JsonResponse({ 'message': 'Successfully queued scrap task', 'ok': True })
    else:
        return JsonResponse({ 'message': 'Key not provided or invalid', 'ok': False })