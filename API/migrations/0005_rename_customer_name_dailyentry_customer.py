# Generated by Django 4.0.2 on 2022-12-13 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0004_alter_customer_date_added_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailyentry',
            old_name='customer_name',
            new_name='customer',
        ),
    ]
