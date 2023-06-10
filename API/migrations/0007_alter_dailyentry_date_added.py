# Generated by Django 4.0.2 on 2023-02-25 13:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_alter_dailyentry_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyentry',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]