# Generated by Django 4.2 on 2024-05-15 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dailyentry', '0011_alter_customer_daily_entry_partition_date_added'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='customer_daily_entry_partition',
            table='customer_daily_entry_partition',
        ),
    ]
