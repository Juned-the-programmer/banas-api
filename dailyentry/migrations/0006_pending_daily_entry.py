# Generated by Django 4.2 on 2023-12-17 13:42

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_alter_customer_email'),
        ('dailyentry', '0005_alter_customer_daily_entry_monthly_customer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='pending_daily_entry',
            fields=[
                ('coolers', models.IntegerField(blank=True, default=0, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
        ),
    ]
