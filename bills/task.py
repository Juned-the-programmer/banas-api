from celery import shared_task
from banas.cache_conf import *
from dailyentry.models import *
from customer.models import CustomerAccount
from .models import CustomerBill
import datetime
from datetime import timedelta
from django.utils import timezone

@shared_task
def run_monthly_task():
    now = timezone.now()

    if now.day == now.monthrange(now.year, now.month)[1]:
        generate_bill_at_the_end_of_month.apply_async()

@shared_task
def generate_bill_at_the_end_of_month():
    #today date
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()

    for instance in customer_cached_data():
        customer_daily_entry = customer_daily_entry_monthly.objects.get(customer=instance.id)
        customer_account = CustomerAccount.objects.get(customer_name=instance.id)

        coolers_total = customer_daily_entry.coolers
        customer_due = customer_account.due

        CustomerBill.objects.create(
            customer_name=instance,
            from_date=first_date,
            to_date=last_date.date(),
            coolers=coolers_total,
            Rate=int(instance.rate),
            Amount=int(coolers_total) * int(instance.rate),
            Pending_amount=int(customer_due),
            Advanced_amount=int(0),
            Total=int(coolers_total) * int(instance.rate) + int(customer_due),
            addedby="Automation Task"
        )

        customer_account.due = int(coolers_total) * int(instance.rate) + int(customer_due)
        customer_account.save()

        customer_daily_entry.coolers = 0
        customer_daily_entry.save()
        