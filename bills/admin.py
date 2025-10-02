from django.contrib import admin

from .models import Bill_number_generator, CustomerBill

# Register your models here.
admin.site.register(CustomerBill)
admin.site.register(Bill_number_generator)
