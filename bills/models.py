from django.db import models
from customer.models import Customer
import uuid

# Create your models here.
class CustomerBill(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True, related_name="customer_bill")
    bill_number = models.CharField(max_length=20, null=True, blank=True)
    from_date = models.CharField(max_length=20)
    to_date = models.CharField(max_length=20)
    coolers = models.IntegerField(default=0, null=True, blank=True)
    Rate = models.IntegerField(default=0, null=True, blank=True)
    Amount = models.IntegerField(default=0, null=True , blank=True)
    Pending_amount = models.IntegerField(default=0, null=True , blank=True)
    Advanced_amount = models.IntegerField(default=0, null=True , blank=True)
    Total = models.IntegerField(default=0, null=True , blank=True)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False, null=True, blank=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100,null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return f"{self.customer_name} - {self.bill_number}"

    class Meta():
        index_together = [['id', 'customer_name', 'bill_number']]

class Bill_number_generator(models.Model):
    bill_number = models.IntegerField()
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.bill_number)