# Generated by Django 4.0.2 on 2022-02-14 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0020_customerbill_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='time',
            field=models.TimeField(auto_now_add=True, default='12:34'),
            preserve_default=False,
        ),
    ]
