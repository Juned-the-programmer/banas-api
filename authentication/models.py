import uuid

from django.db import models

# Create your models here.
# class Dashboard(models.Model):
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)
#     date = models.DateTimeField(auto_now_add=False)
#     coolers = models.IntegerField(default=0, null=True, blank=True)
#     total_customer = models.IntegerField(default=0, blank=True, null=True)
#     total_pending_daily_entry = models.IntegerField(default=0, blank=True, null=True)
#     total_bill_month = models.IntegerField(default=0, blank=True, null=True)
