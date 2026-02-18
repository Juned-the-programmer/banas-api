from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DailyEntry, DailyEntry_dashboard, customer_daily_entry_monthly


@receiver(post_save, sender=DailyEntry)
def update_customer_daily_entry(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created and instance.customer:
        # Use get_or_create to handle cases where the record doesn't exist
        customer_detail, _ = customer_daily_entry_monthly.objects.get_or_create(
            customer=instance.customer,
            defaults={"coolers": 0}
        )
        customer_detail.coolers += int(instance.cooler)
        customer_detail.save()

        # Update today daily Entry dashboard
        dashboard_detail = DailyEntry_dashboard.objects.first()
        if dashboard_detail:
            dashboard_detail.customer_count += 1
            dashboard_detail.coolers_count += int(instance.cooler)
            dashboard_detail.save()
        else:
            # Create dashboard if it doesn't exist
            DailyEntry_dashboard.objects.create(
                customer_count=1,
                coolers_count=int(instance.cooler)
            )


post_save.connect(update_customer_daily_entry, sender=DailyEntry)
