# Generated by Django 3.2.5 on 2021-08-02 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0003_rename_code_record_currency_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='prev_rate',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True),
        ),
    ]
