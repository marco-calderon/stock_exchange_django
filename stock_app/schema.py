from stock_app.models import Record
from graphene import ObjectType, String, Schema, Field, List, Decimal, Int
from graphene_django import DjangoObjectType
from datetime import datetime, timedelta

class RecordType(DjangoObjectType):
    source_currency_code = Field(String)
    currency_code = Field(String)
    prev_rate = Field(Decimal)
    difference = Field(Decimal)

    class Meta:
        model = Record
        fields = ('id', 'date', 'source_currency_code', 'currency_code', 'rate', 'prev_rate', 'difference')

    def resolve_source_currency_code(self, info):
        if self.other is not None:
            return self.other.currency_code[2:5]
        else:
            return 'USD'

    def resolve_currency_code(self, info):
        return self.currency_code[2:5]

    def resolve_prev_rate(self, info):
        try:
            if self.other is not None:
                return self.other.prev_rate / self.prev_rate
            else:
                return self.prev_rate
        except Exception:
            return None

    def resolve_difference(self, info):
        try:
            if self.other is not None:
                return self.rate - (self.other.prev_rate / self.prev_rate)
            else:
                return self.rate / self.prev_rate
        except Exception:
            return None

class Query(ObjectType):
    week_records = List(RecordType, code_from=String(default_value="USD"), code_to=String(default_value="MXN"))
    comparison_records = List(
        RecordType,
        code_from=String(default_value="USD"),
        code_to=String(default_value="MXN"),
        start_timestamp=Int(),
        end_timestamp=Int()
    )

    def resolve_week_records(root, info, code_from, code_to):
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        end_date = start_date + timedelta(days=7)
        week_from_records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_from)).order_by('-date')
        week_to_records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_to)).order_by('-date')
        week_records = []
        
        for from_record in week_from_records:
            start = from_record.date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            to_records = list(filter(lambda to_record: start <= to_record.date and end >= to_record.date, week_to_records))
            if len(to_records) > 0:
                to_record = to_records[0]
                if code_from != 'USD':
                    to_record.rate = from_record.rate / to_record.rate
                    to_record.other = from_record
                week_records.append(to_record)

        return week_records

    def resolve_comparison_records(root, info, code_from, code_to, start_timestamp, end_timestamp):
        start_date = datetime.fromtimestamp(start_timestamp)
        end_date = datetime.fromtimestamp(end_timestamp)
        week_from_records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_from)).order_by('-date')
        week_to_records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_to)).order_by('-date')
        week_records = []
        
        for from_record in week_from_records:
            start = from_record.date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            to_records = list(filter(lambda to_record: start <= to_record.date and end >= to_record.date, week_to_records))
            if len(to_records) > 0:
                to_record = to_records[0]
                if code_from != 'USD':
                    to_record.rate = from_record.rate / to_record.rate
                    to_record.other = from_record
                week_records.append(to_record)

        return week_records

schema = Schema(query=Query)