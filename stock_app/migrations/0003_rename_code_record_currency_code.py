# Generated by Django 3.2.5 on 2021-07-07 00:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0002_alter_record_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='code',
            new_name='currency_code',
        ),
    ]
