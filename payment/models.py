import uuid

from django.db import models
from django.db.models.base import ModelBase

from customer.models import Customer


# Create your models here.
class CustomerPayment(models.Model):
    customer_name = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_payment"
    )
    pending_amount = models.IntegerField(null=True, blank=True)
    paid_amount = models.IntegerField()
    rounf_off_amount = models.IntegerField(default=0, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    addedby = models.CharField(max_length=100, null=True, blank=True)
    updatedby = models.CharField(max_length=100, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.customer_name)

    class Meta:
        index_together = [["id", "customer_name"]]


# class PartitionedModelBase(ModelBase):
#     def __new__(cls, name, bases, attrs, **kwargs):
#         # Get the base model
#         base_model = super().__new__(cls, name, bases, attrs, **kwargs)

#         # Check if the model is direct subclass of PartitionModel
#         if bases and bases[0].__name__ == 'PartitionedModel':
#             # set the db_table attribue based on the year and month
#             base_model._meta.db_table = name.lower()

#         return base_model

# class PartitionedModel(models.Model, metaclass=PartitionedModelBase):
#     date = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         abstract = True

# class customer_payment(PartitionedModel):
#     customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True, related_name="customer_payments_partitioned")
#     pending_amount = models.IntegerField(null=True, blank=True)
#     paid_amount = models.IntegerField()
#     rounf_off_amount = models.IntegerField(default=0, null=True, blank=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100,null=True, blank=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.customer_name)
