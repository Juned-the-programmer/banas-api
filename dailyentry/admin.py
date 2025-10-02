from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(DailyEntry)
admin.site.register(customer_daily_entry_monthly)
admin.site.register(customer_qr_code)
admin.site.register(pending_daily_entry)
admin.site.register(DailyEntry_dashboard)
