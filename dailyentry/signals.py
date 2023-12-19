from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from bulk_signals import signals
from .task import update_customer_daily_entry_to_monthly_table_bulk

@receiver(post_save, sender=DailyEntry)
def update_customer_daily_entry(sender, instance, created, **kwargs):
    if created:
        customer_detail = customer_daily_entry_monthly.objects.get(customer=instance.customer)
        customer_detail.coolers += int(instance.cooler)
        customer_detail.save()

@receiver(signals.post_bulk_create, sender=DailyEntry)
def update_customer_daily_entry_bulk(sender, **kwargs):
    daily_entries = kwargs["objects"]
    update_customer_daily_entry_to_monthly_table_bulk.delay(daily_entries)

post_save.connect(update_customer_daily_entry, sender=DailyEntry)