# Generated by Django 4.0.2 on 2022-02-07 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0014_customerbill'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerbill',
            name='from_date',
            field=models.CharField(default='juned', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerbill',
            name='to_date',
            field=models.CharField(default='juned', max_length=20),
            preserve_default=False,
        ),
    ]
