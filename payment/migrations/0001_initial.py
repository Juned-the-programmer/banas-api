# Generated by Django 4.0.2 on 2023-06-12 14:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerPayment',
            fields=[
                ('pending_amount', models.IntegerField(blank=True, null=True)),
                ('paid_amount', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('customer_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.customer')),
            ],
        ),
    ]