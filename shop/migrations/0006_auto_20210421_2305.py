# Generated by Django 3.1.7 on 2021-04-21 17:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20210421_2305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='cmt_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 21, 23, 5, 36, 493737)),
        ),
        migrations.AlterField(
            model_name='comments',
            name='edit_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 21, 23, 5, 36, 493737)),
        ),
    ]
