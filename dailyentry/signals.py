from bulk_signals import signals
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *
from .task import update_customer_daily_entry_to_monthly_table_bulk


@receiver(post_save, sender=DailyEntry)
def update_customer_daily_entry(sender, instance, created, **kwargs):
    if created:
        customer_detail = customer_daily_entry_monthly.objects.get(customer=instance.customer)
        customer_detail.coolers += int(instance.cooler)
        customer_detail.save()

        # Update today daily Entry dashboard
        dashboard_detail = DailyEntry_dashboard.objects.first()
        dashboard_detail.customer_count += 1
        dashboard_detail.coolers_count += int(instance.cooler)
        dashboard_detail.save()


@receiver(signals.post_bulk_create, sender=DailyEntry)
def update_customer_daily_entry_bulk(sender, **kwargs):
    daily_entries = kwargs["objects"]
    entry_data_list = [{"customer_id": entry.customer.id, "cooler": entry.cooler} for entry in daily_entries]
    update_customer_daily_entry_to_monthly_table_bulk.delay(entry_data_list)


post_save.connect(update_customer_daily_entry, sender=DailyEntry)
