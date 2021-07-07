from stock_app.models import Record
from graphene import ObjectType, String, Schema, Mutation, Field, List
from graphene_django import DjangoObjectType
from datetime import datetime, timedelta

class RecordType(DjangoObjectType):
    currency_code = Field(String)
    class Meta:
        model = Record
        fields = ('id', 'date', 'currency_code', 'rate')

    def resolve_currency_code(self, info):
        return self.currency_code[2:5]

class Query(ObjectType):
    week_records = List(RecordType, code_from=String(default_value="USD"), code_to=String(default_value="MXN"))

    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response
    def resolve_week_records(root, info, code_from, code_to):
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        end_date = start_date + timedelta(days=8)

        week_records = Record.objects.filter(date__gte=start_date, date__lte=end_date, currency_code="('{0}',)".format(code_to))

        return week_records

schema = Schema(query=Query)