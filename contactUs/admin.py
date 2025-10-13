from django.contrib import admin

from .models import Contact


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "message", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "phone", "message"]
    readonly_fields = ["id", "created_at"]
