import datetime

from django.db.models import Sum
from django_cron import CronJobBase, Schedule

from customer.models import Customer, CustomerAccount
from dailyentry.models import DailyEntry
from route.models import Route
import calendar

from .models import CustomerBill


class Generate_CustomerBill_CronJobs(CronJobBase):
    RUN_EVERY_MINS = 60 * 12
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "bills.generate_customer_bills_cron_job" 
    
    def do(self):
        today = datetime.date.today()
        _, last_day = calendar.monthrange(today.year, today.month)
        last_day_of_month = datetime.date(today.year, today.month, last_day)
        first_day_of_month = first_day_of_month = today.replace(day=1)
        if today == last_day_of_month:
            customers = Customer.objects.all().exclude(active=False)
            
            for customer in customers:
                daily_entry_records = DailyEntry.objects.filter(date_added__gte=first_day_of_month).filter(date_added__lte=last_day_of_month).filter(customer=customer).aggregate(Sum('cooler'))
                daily_entry_total = daily_entry_records['cooler__sum']
                if daily_entry_total is None:
                    coolers = 0
                else:
                    coolers = int(daily_entry_total)
                    
                pending_amount = CustomerAccount.objects.get(customer_name=customer)
                    
                CustomerBill.objects.create(
                    customer_name=customer,
                    from_date=first_day_of_month,
                    to_date=last_day_of_month,
                    coolers=coolers,
                    Rate=int(customer.rate),
                    Amount=int(coolers) * int(customer.rate),
                    Pending_amount=int(pending_amount.due),
                    Advanced_amount=int(0),
                    Total=int(coolers) * int(customer.rate) + int(pending_amount.due),
                    addedby="Crone Job"
                )
                
                pending_amount.due = int(coolers) * int(customer.rate) + int(pending_amount.due)
                pending_amount.save()