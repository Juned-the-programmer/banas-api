# Generated by Django 4.0.2 on 2022-12-13 19:05

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('name', models.CharField(max_length=200)),
                ('rate', models.IntegerField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('expanded', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('route_name', models.CharField(max_length=100)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DailyEntry',
            fields=[
                ('cooler', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerPayment',
            fields=[
                ('pending_amount', models.IntegerField()),
                ('paid_amount', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('customer_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerBill',
            fields=[
                ('from_date', models.CharField(max_length=20)),
                ('to_date', models.CharField(max_length=20)),
                ('coolers', models.IntegerField(blank=True, default=0, null=True)),
                ('Rate', models.IntegerField(blank=True, default=0, null=True)),
                ('Amount', models.IntegerField(blank=True, default=0, null=True)),
                ('Pending_amount', models.IntegerField(blank=True, default=0, null=True)),
                ('Advanced_amount', models.IntegerField(blank=True, default=0, null=True)),
                ('Total', models.IntegerField(blank=True, default=0, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('paid', models.BooleanField(blank=True, default=False, null=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('customer_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerAccount',
            fields=[
                ('due', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('addedby', models.CharField(blank=True, max_length=100, null=True)),
                ('updatedby', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('customer_name', models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='route',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_route', to='API.route'),
        ),
    ]
