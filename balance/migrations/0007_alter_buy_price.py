# Generated by Django 5.2.3 on 2025-07-21 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balance', '0006_buy_orderbuy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buy',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
