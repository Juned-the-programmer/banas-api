# Generated by Django 4.2 on 2024-02-16 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0008_alter_customer_index_together_and_more'),
        ('bills', '0002_alter_customerbill_customer_name'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='customerbill',
            index_together={('id', 'customer_name')},
        ),
    ]