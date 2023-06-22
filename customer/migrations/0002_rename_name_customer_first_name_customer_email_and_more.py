# Generated by Django 4.0.2 on 2023-06-21 13:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, validators=[django.core.validators.EmailValidator(message='Enter Valid Email address')]),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_name',
            field=models.CharField(default='Juned', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='phone_no',
            field=models.CharField(blank=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Invalid phone number', regex='^[789]\\d{9}$')]),
        ),
    ]