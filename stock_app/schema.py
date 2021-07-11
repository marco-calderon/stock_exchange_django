from stock_app.models import Record
from graphene import ObjectType, String, Schema, Mutation, Field, List, Decimal, DateTime, Int
from graphene_django import DjangoObjectType
from datetime import datetime, timedelta

class RecordType(DjangoObjectType):
    currency_code = Field(String)
    prev_rate = Field(Decimal)
    difference = Field(Decimal)

    class Meta:
        model = Record
        fields = ('id', 'date', 'currency_code', 'rate', 'prev_rate', 'difference')

    def resolve_currency_code(self, info):
        return self.currency_code[2:5]

    def resolve_prev_rate(self, info):
        start_date = self.date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        prev_record = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code=self.currency_code)
        if len(prev_record) > 0:
            return prev_record[0].rate
        else:
            return 0

    def resolve_difference(self, info):
        start_date = self.date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        prev_record = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code=self.currency_code)
        if len(prev_record) > 0:
            return self.rate - prev_record[0].rate
        else:
            return 0

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
        end_date = start_date + timedelta(days=8)
        week_records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_to))
        return week_records

    def resolve_comparison_records(root, info, code_from, code_to, start_timestamp, end_timestamp):
        start_date = datetime.fromtimestamp(start_timestamp)
        end_date = datetime.fromtimestamp(end_timestamp)
        records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_to))
        return records

schema = Schema(query=Query)