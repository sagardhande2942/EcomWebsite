# Generated by Django 3.1.7 on 2021-04-16 07:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20210415_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasedate',
            name='purd',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 16, 13, 13, 24, 675194), null=True),
        ),
    ]