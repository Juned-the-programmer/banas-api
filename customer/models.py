from django.db import models
from route.models import Route
import uuid
from django.db.models.signals import post_save
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^[789]\d{9}$',
        message="Invalid phone number"
    )
    email_validator = EmailValidator(
        message="Enter Valid Email address"
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_no = models.CharField(max_length=10, validators=[phone_regex], null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE , null=True, blank=True , related_name="customer_route")
    email = models.EmailField(validators=[email_validator], null=True, blank=True)
    rate = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100,null=True, blank=True)
    active = models.BooleanField(default=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_added = timezone.now()
        
        self.date_updated = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

class CustomerAccount(models.Model):
    customer_name = models.OneToOneField(Customer, on_delete = models.CASCADE , null=True, blank=True , related_name="customer_account")
    due = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100,null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)

    def __str__(self):
        return str(self.customer_name)