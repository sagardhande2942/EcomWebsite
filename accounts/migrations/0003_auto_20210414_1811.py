# Generated by Django 3.1.7 on 2021-04-14 12:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_extendeduser_totcarts'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purdate', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.AddField(
            model_name='extendeduser',
            name='pur',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.purchasedate'),
        ),
    ]
