from django.db import models
from customer.models import Customer
import uuid

# Create your models here.
class DailyEntry(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null=True, blank=True)
    cooler = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100,null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.customer)