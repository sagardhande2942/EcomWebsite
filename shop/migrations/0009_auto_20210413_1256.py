# Generated by Django 3.1.7 on 2021-04-13 07:26

from django.db import migrations
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_auto_20210311_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=s3direct.fields.S3DirectField(default=''),
        ),
    ]