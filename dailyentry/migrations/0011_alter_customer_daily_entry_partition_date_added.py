# Generated by Django 4.2 on 2024-04-26 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailyentry', '0010_customer_daily_entry_partition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_daily_entry_partition',
            name='date_added',
            field=models.DateTimeField(),
        ),
    ]
