# Generated by Django 5.2.3 on 2025-07-01 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='service_price',
            new_name='service',
        ),
    ]
