# Generated by Django 3.1.7 on 2021-04-19 13:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasedate',
            name='purd',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 19, 18, 52, 39, 633096), null=True),
        ),
    ]