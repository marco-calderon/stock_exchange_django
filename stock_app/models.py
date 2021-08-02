from django.db import models

class Record(models.Model):
    date = models.DateTimeField()
    currency_code = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=20, decimal_places=10)
    prev_rate = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    difference = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    other = None

    def to_dict(self):
        return {
            'id': self.pk,
            'date': self.date,
            'currency_code': self.currency_code,
            'rate': self.rate,
            'prev_rate': self.prev_rate,
            'difference': self.difference
        }

    def __repr__(self):
        return '[{0}] {1} - currency_code: {2}, rate {3}'.format(self.pk, self.date, self.currency_code, self.rate)


    def __str__(self):
        return '[{0}] {1} - currency_code: {2}, rate {3}'.format(self.pk, self.date, self.currency_code, self.rate)
        
    class Meta:
        db_table = 'entries'