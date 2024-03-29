# Generated by Django 4.2 on 2023-12-17 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_alter_customer_email'),
        ('dailyentry', '0004_customer_qr_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_daily_entry_monthly',
            name='customer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.customer'),
        ),
        migrations.AlterField(
            model_name='customer_qr_code',
            name='customer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.customer'),
        ),
    ]
