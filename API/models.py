# from django.db import models
# import uuid
# from django.db.models.signals import post_save

# # Create your models here.
# class Route(models.Model):
#     route_name = models.CharField(max_length=100)
#     date_added = models.DateTimeField(auto_now_add=True)
#     date_updated = models.DateTimeField(auto_now=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100, null=True, blank=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.route_name)

# class Customer(models.Model):
#     name = models.CharField(max_length=200)
#     route = models.ForeignKey(Route, on_delete=models.CASCADE , null=True, blank=True , related_name="customer_route")
#     rate = models.IntegerField()
#     date_added = models.DateTimeField(auto_now_add=True)
#     date_updated = models.DateTimeField(auto_now_add=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100,null=True, blank=True)
#     active = models.BooleanField(default=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.name)

# class CustomerAccount(models.Model):
#     customer_name = models.ForeignKey(Customer, on_delete = models.CASCADE , null=True, blank=True , default=0)
#     due = models.IntegerField(default=0)
#     date = models.DateTimeField(auto_now_add=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100,null=True, blank=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.customer_name)

# class CustomerPayment(models.Model):
#     customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True)
#     pending_amount = models.IntegerField(null=True, blank=True)
#     paid_amount = models.IntegerField()
#     date = models.DateTimeField(auto_now_add=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100,null=True, blank=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.customer_name)

# class DailyEntry(models.Model):
#     customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null=True, blank=True)
#     cooler = models.IntegerField()
#     date_added = models.DateTimeField(auto_now_add=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100,null=True, blank=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.customer)

# class CustomerBill(models.Model):
#     customer_name = models.ForeignKey(Customer, on_delete = models.SET_NULL , null=True, blank=True)
#     from_date = models.CharField(max_length=20)
#     to_date = models.CharField(max_length=20)
#     coolers = models.IntegerField(default=0, null=True, blank=True)
#     Rate = models.IntegerField(default=0, null=True, blank=True)
#     Amount = models.IntegerField(default=0, null=True , blank=True)
#     Pending_amount = models.IntegerField(default=0, null=True , blank=True)
#     Advanced_amount = models.IntegerField(default=0, null=True , blank=True)
#     Total = models.IntegerField(default=0, null=True , blank=True)
#     date = models.DateTimeField(auto_now_add=True)
#     paid = models.BooleanField(default=False, null=True, blank=True)
#     addedby = models.CharField(max_length=100,null=True, blank=True)
#     updatedby = models.CharField(max_length=100,null=True, blank=True)
#     id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

#     def __str__(self):
#         return str(self.customer_name)


# def customer_account(sender , instance , created , **kwargs):
#     if created:
#         CustomerAccount.objects.create(customer_name = instance)

# post_save.connect(customer_account,sender=Customer)
