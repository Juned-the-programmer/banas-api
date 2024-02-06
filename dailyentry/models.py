from django.db import models
from customer.models import Customer
import uuid

# Create your models here.
class DailyEntry(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null=True, blank=True, related_name="customer_daily_entry")
    cooler = models.IntegerField()
    date_added = models.DateTimeField(null=True, blank=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100,null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.customer)

    class Meta():
        index_together = [['id', 'customer']]

class DailyEntry_dashboard(models.Model):
    customer_count = models.IntegerField(default=0, null=True, blank=True)
    coolers_count = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.customer_count)
    
class customer_daily_entry_monthly(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    coolers = models.IntegerField(default=0)

    def __str__(self):
        return str(self.customer)

    class Meta():
        index_together = [['customer']]

class customer_qr_code(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    qrcode = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    qrcode_pin = models.IntegerField(default=1234, null=True, blank=True)

    def __str__(self):
        return str(self.customer)

    class Meta():
        index_together = [['customer']]

class pending_daily_entry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    coolers = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.customer)
    
    class Meta():
        index_together = [['id', 'customer']]