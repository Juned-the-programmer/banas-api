from django.contrib import admin
from drf_api_logger.models import APILogsModel

@admin.register(APILogsModel)
class APILogsAdmin(admin.ModelAdmin):
    list_display = ("api", "status_code", "execution_time", "created")
    search_fields = ("api", "headers", "body", "method", "status_code")
    list_filter = ("method", "status_code", "created")