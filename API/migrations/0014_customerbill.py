# Generated by Django 4.0.2 on 2022-02-07 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0013_alter_customeraccount_due'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerBill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coolers', models.IntegerField(blank=True, default=0, null=True)),
                ('Rate', models.IntegerField(blank=True, default=0, null=True)),
                ('Amount', models.IntegerField(blank=True, default=0, null=True)),
                ('Pending_amount', models.IntegerField(blank=True, default=0, null=True)),
                ('Advanced_amount', models.IntegerField(blank=True, default=0, null=True)),
                ('Total', models.IntegerField(blank=True, default=0, null=True)),
                ('customer_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.customer')),
            ],
        ),
    ]