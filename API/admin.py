from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Route)
admin.site.register(DailyEntry)
admin.site.register(CustomerPayment)
admin.site.register(CustomerAccount)