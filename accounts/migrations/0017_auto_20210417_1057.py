# Generated by Django 3.1.7 on 2021-04-17 05:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20210417_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchasedate',
            name='lango',
        ),
        migrations.AlterField(
            model_name='purchasedate',
            name='purd',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 17, 10, 57, 36, 296446), null=True),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField(default=0, null=True)),
                ('rating', models.IntegerField(default=1, null=True)),
                ('rateusers', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.extendeduser')),
            ],
        ),
    ]