# Generated by Django 3.1.7 on 2021-04-16 19:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20210417_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasedate',
            name='purd',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 17, 1, 1, 20, 758254), null=True),
        ),
    ]
