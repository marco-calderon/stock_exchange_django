import environ
from open_exchange_rates import OpenExchangeRates
from django.shortcuts import render
from .models import Record
from datetime import datetime, timedelta
from django.http import JsonResponse

# Create your views here.
def scrap(request):
    env = environ.Env()
    secret = env('TOKEN')
    if ('key' in request.GET and request.GET['key'] == secret):
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(hours=23, minutes=59)

        results = Record.objects.filter(date__gte=start_date, date__lte=end_date).first()
        if results is not None:
            return
        
        api = OpenExchangeRates()
        data = api.get_today()

        if data['rates']:
            codes = list(data['rates'].keys())
            for code in codes:
                r = Record()
                r.date = datetime.now()
                r.currency_code = code,
                r.rate = float(data['rates'][code])
                r.save()
        return JsonResponse({ 'message': 'Successfully saved', 'ok': True })
    else:
        return JsonResponse({ 'message': 'Key not provided or invalid', 'ok': False })