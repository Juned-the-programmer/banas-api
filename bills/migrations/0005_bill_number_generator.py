# Generated by Django 4.2 on 2024-04-26 12:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0004_alter_customerbill_index_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill_number_generator',
            fields=[
                ('bill_number', models.IntegerField()),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
            ],
        ),
    ]