from calendar import monthrange
import datetime
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from banas.cache_conf import customer_cached_data
from bills.utils import bill_number_generator
from customer.models import CustomerAccount
from dailyentry.models import customer_daily_entry_monthly

from .models import Bill_number_generator, CustomerBill


@shared_task
def run_monthly_task():
    now = timezone.now()

    if now.day == monthrange(now.year, now.month)[1]:
        generate_bill_at_the_end_of_month.apply_async()


@shared_task
def generate_bill_at_the_end_of_month():
    # today date
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()

    # Bill number
    bill_number = bill_number_generator()
    last_four_digits = bill_number[-4:]

    for instance in customer_cached_data():
        customer_daily_entry = customer_daily_entry_monthly.objects.get(customer=instance.id)
        customer_account = CustomerAccount.objects.get(customer_name=instance.id)

        coolers_total = customer_daily_entry.coolers
        customer_due = customer_account.due

        new_last_four_digits = str(int(last_four_digits) + 1).zfill(4)
        new_bill_number = bill_number[:-4] + new_last_four_digits
        last_four_digits = new_last_four_digits

        CustomerBill.objects.create(
            bill_number=str(new_bill_number),
            customer_name=instance,
            from_date=first_date,
            to_date=last_date.date(),
            coolers=coolers_total,
            Rate=int(instance.rate),
            Amount=int(coolers_total) * int(instance.rate),
            Pending_amount=int(customer_due),
            Advanced_amount=int(0),
            Total=int(coolers_total) * int(instance.rate) + int(customer_due),
            addedby="Automation Task",
        )

        customer_account.due = int(coolers_total) * int(instance.rate) + int(customer_due)
        customer_account.save()

        customer_daily_entry.coolers = 0
        customer_daily_entry.save()

    Bill_number_generator.objects.all().delete()
