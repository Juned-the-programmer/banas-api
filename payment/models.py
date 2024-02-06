from django.db import models
from customer.models import Customer
import uuid

# Create your models here.
class CustomerPayment(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True, related_name="customer_payment")
    pending_amount = models.IntegerField(null=True, blank=True)
    paid_amount = models.IntegerField()
    rounf_off_amount = models.IntegerField(default=0, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100,null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.customer_name)

    class Meta():
        index_together = [['id', 'customer_name']]