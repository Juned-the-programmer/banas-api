# Generated by Django 4.2 on 2023-12-21 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailyentry', '0007_alter_dailyentry_date_added'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyEntry_dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_count', models.IntegerField(blank=True, default=0, null=True)),
                ('coolers_count', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
    ]
