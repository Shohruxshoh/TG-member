# Generated by Django 5.2.3 on 2025-07-25 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0007_rename_kanal_name_link_channel_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='country_code',
            field=models.CharField(default=1, max_length=200, unique=True),
            preserve_default=False,
        ),
    ]
