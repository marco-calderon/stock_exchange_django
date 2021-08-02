from open_exchange_rates import OpenExchangeRates
import click
import logging
import os
from datetime import datetime, timedelta
import django
import json

# Configure Django for using models outside app.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_exchange_django.settings")
django.setup()


LOG_DIR = 'logs'


# Configuration to save the logs into a file
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)
logging.basicConfig(filename='{0}/{1}.log'.format(LOG_DIR, datetime.now().strftime('%Y%m%d_%H%M')), level=logging.DEBUG)


@click.group()
def main():
    pass


@main.group('database')
def database():
    pass


@database.command('update')
def update():
    from stock_app.models import Record

    logging.info('Updating today exchange rates...')
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(hours=23, minutes=59)
    logging.debug('start_date used: {0}'.format(start_date.isoformat()))

    results = Record.objects.filter(date__gte=start_date, date__lte=end_date).first()
    if results is not None:
        logging.info('Records are present for today. Skipping...')
        print('Records are present for today. Skipping...')
        return
    
    api = OpenExchangeRates()
    data = api.get_today()
    logging.info(json.dumps(data))

    if data['rates']:
        logging.info('Adding records for today')
        print('Adding records for today')
        codes = list(data['rates'].keys())
        for code in codes:
            r = Record()
            r.date = datetime.now()
            r.currency_code = code,
            r.rate = float(data['rates'][code])
            r.save()
        logging.info('Added {0} records.'.format(len(codes)))
        print('Added {0} records.'.format(len(codes)))


@database.command('fix')
def fix():
    from stock_app.models import Record

    all_records = Record.objects.all()
    for record in all_records:
        logging.info('Trying to update record {0}.'.format(str(record)))
        print('Trying to update record {0}.'.format(str(record)))

        # Filtering params for last day
        start_date = record.date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        prev_rate = 0.0
        difference = 0.0

        try:
            # Gets the previous entry
            prev_record = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code=record.currency_code)[0]
            
            if prev_record is not None:
                # Update if found
                prev_rate = prev_record.rate
                difference = record.rate - prev_record.rate
                record.prev_rate = prev_rate
                record.difference = difference
                record.save()
                logging.info('Updated record {0}.'.format(str(record)))
                print('Updated record {0}.'.format(str(record)))
            else:
                logging.info('Not found prev record for {0}.'.format(str(record)))
                print('Not found prev record for {0}.'.format(str(record)))

        except Exception:
            logging.info('Not found prev record for {0}.'.format(str(record)))
            print('Not found prev record for {0}.'.format(str(record)))


if __name__ == "__main__":
    main()