# Generated by Django 4.2 on 2024-04-26 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_customer_payment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Customer_payment',
        ),
    ]
