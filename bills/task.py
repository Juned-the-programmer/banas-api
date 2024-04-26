from celery import shared_task
from banas.cache_conf import *
from dailyentry.models import *
from customer.models import CustomerAccount
from .models import CustomerBill, Bill_number_generator
import datetime
from datetime import timedelta
from django.utils import timezone
from calendar import monthrange

@shared_task
def run_monthly_task():
    now = timezone.now()

    if now.day == monthrange(now.year, now.month)[1]:
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
            addedby="Automation Task"
        )

        customer_account.due = int(coolers_total) * int(instance.rate) + int(customer_due)
        customer_account.save()

        customer_daily_entry.coolers = 0
        customer_daily_entry.save()

    
    Bill_number_generator.objects.all().delete()


def bill_number_generator():

    # For Bill Number
    today = datetime.date.today()
    year = today.strftime("%Y")
    month = today.strftime("%m")

    # Last Bill Number
    last_bill = Bill_number_generator.objects.all().first()

    if last_bill:
        last_bill_number = str(last_bill.bill_number)[-4:]
        new_bill_number = str(int(last_bill_number) + 1).zfill(4)
    else:
        new_bill_number = "0001"
        bill_number = Bill_number_generator.objects.create(
            bill_number = f"{year}{month}{new_bill_number}"
        )
        bill_number.save()

    return f"{year}{month}{new_bill_number}"