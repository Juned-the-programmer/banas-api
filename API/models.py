from django.db import models
import uuid
from django.db.models.signals import post_save

# Create your models here.
class Route(models.Model):
    route_name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.route_name)

class Customer(models.Model):
    name = models.CharField(max_length=200)
    route = models.ForeignKey(Route, on_delete= models.SET_NULL , null=True, blank=True , related_name="customer_route")
    rate = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.name)

class DailyEntry(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL, null=True, blank=True)
    cooler = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.customer_name)

class CustomerAccount(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True , default=0)
    due = models.IntegerField()

    def __str__(self):
        return str(self.customer_name.name)

class CustomerPayment(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True)
    pending_amount = models.IntegerField()
    paid_amount = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.customer_name.name)

def customer_account(sender , instance , created , **kwargs):
    if created:
        CustomerAccount.objects.create(customer_name = instance)

post_save.connect(customer_account,sender=Customer)
