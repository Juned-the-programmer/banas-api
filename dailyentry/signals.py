from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=DailyEntry)
def update_customer_daily_entry(sender, instance, created, **kwargs):
    if created:
        customer_detail = customer_daily_entry_monthly.objects.get(customer=instance.customer)
        customer_detail.coolers += int(instance.cooler)
        customer_detail.save()

post_save.connect(update_customer_daily_entry, sender=DailyEntry)