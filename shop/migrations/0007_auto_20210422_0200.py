# Generated by Django 3.1.7 on 2021-04-21 20:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_auto_20210421_2305'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search', models.CharField(blank=True, default='', max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='comments',
            name='cmt_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 22, 2, 0, 20, 978172)),
        ),
        migrations.AlterField(
            model_name='comments',
            name='edit_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 22, 2, 0, 20, 978172)),
        ),
    ]
