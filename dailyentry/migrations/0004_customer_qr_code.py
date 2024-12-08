# Generated by Django 4.2 on 2023-12-17 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_alter_customer_email'),
        ('dailyentry', '0003_customer_daily_entry_monthly'),
    ]

    operations = [
        migrations.CreateModel(
            name='customer_qr_code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qrcode', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('qrcode_pin', models.IntegerField(blank=True, default=1234, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.customer')),
            ],
        ),
    ]
