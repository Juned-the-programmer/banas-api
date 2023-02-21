from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

#Import Export Data
class CustomerAdmin(ImportExportModelAdmin):
    pass

class RouteAdmin(ImportExportModelAdmin):
    pass

class DailyEntryAdmin(ImportExportModelAdmin):
    pass

class CustomerPaymentAdmin(ImportExportModelAdmin):
    pass

class CustomerAccountAdmin(ImportExportModelAdmin):
    pass

class CustomerBillAdmin(ImportExportModelAdmin):
    pass

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Route , RouteAdmin)
admin.site.register(DailyEntry , DailyEntryAdmin)
admin.site.register(CustomerPayment , CustomerPaymentAdmin)
admin.site.register(CustomerAccount , CustomerAccountAdmin)
admin.site.register(CustomerBill , CustomerBillAdmin)