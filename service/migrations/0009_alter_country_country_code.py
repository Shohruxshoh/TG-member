# Generated by Django 5.2.3 on 2025-07-25 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0008_country_country_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='country_code',
            field=models.CharField(max_length=200),
        ),
    ]
