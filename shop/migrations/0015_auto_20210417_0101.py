# Generated by Django 3.1.7 on 2021-04-16 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_auto_20210417_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.IntegerField(default=1, null=True),
        ),
    ]