import datetime
from datetime import date, time, timedelta

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from customer.models import Customer, CustomerAccount
from dailyentry.models import DailyEntry, customer_daily_entry_monthly
from dailyentry.serializer import *
from exception.views import *

from .models import CustomerBill
from .serializer import *
from .task import bill_number_generator
from .utils import get_dynamic_entries

# create your view here


@api_view(["GET"])
@permission_classes([IsAdminUser, IsAuthenticated])
def get_bills(request):
    if request.method == "GET":
        bills = CustomerBill.objects.all()
        customer_bill = GenerateBillSerializerGET(bills, many=True)
        return JsonResponse(customer_bill.data, status=status.HTTP_200_OK, safe=False)

    return internal_server_error()


@api_view(["GET"])
@permission_classes([IsAdminUser, IsAuthenticated])
def bill_detail(request, pk):
    import pytz

    now = timezone.now()
    first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_previous_month = (first_day_of_current_month - timezone.timedelta(days=1)).replace(day=1)
    table_name = f'DailyEntry_{first_day_of_previous_month.strftime("%B_%Y")}'
    if request.method == "GET":
        try:
            bill = CustomerBill.objects.get(pk=pk)
        except CustomerBill.DoesNotExist:
            return bill_not_found_exception(pk)

        customer_bill = GenerateBillSerializerGET(bill)
        customer_name = CustomerBill.objects.get(pk=pk).id

        from_date = bill.from_date
        from_date_month = from_date[5:7]
        from_date_year = from_date[0:4]
        from_date_date = from_date[8:10]

        to_date = bill.to_date
        to_date_month = to_date[5:7]
        to_date_year = to_date[0:4]
        to_date_date = to_date[8:10]

        from_date_new = datetime.datetime(int(from_date_year), int(from_date_month), int(from_date_date), tzinfo=pytz.UTC)

        to_date_new = datetime.datetime(int(to_date_year), int(to_date_month), int(to_date_date), 23, 59, 59, tzinfo=pytz.UTC)

        raw_data = get_dynamic_entries(bill.customer_name.id, from_date_new, to_date_new, table_name)
        daily_entry_serializer = DialyEntrySerializerGETDashboard(raw_data, many=True)

        return JsonResponse(
            {"bill": customer_bill.data, "daily_entry": daily_entry_serializer.data}, status=status.HTTP_200_OK
        )

    return internal_server_error()


@api_view(["POST"])
@permission_classes([IsAdminUser, IsAuthenticated])
def generate_bill(request, pk):
    if request.method == "POST":
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return customer_not_found_exception(pk)

        # today date
        today_date = datetime.datetime.now()

        # Last day of month
        next_month = today_date.replace(day=28) + timedelta(days=4)
        last_date = next_month - timedelta(days=next_month.day)

        # First day of month
        first_date = datetime.datetime.today().replace(day=1).date()

        customer_daily_entry = customer_daily_entry_monthly.objects.get(customer=pk)

        coolers_total = customer_daily_entry.coolers

        customer_account = CustomerAccount.objects.get(customer_name=pk)

        # Bill number
        bill_number = bill_number_generator()
        last_four_digits = bill_number[-4:]
        new_last_four_digits = str(int(last_four_digits) + 1).zfill(4)
        new_bill_number = bill_number[:-4] + new_last_four_digits

        CustomerBill.objects.create(
            bill_number=str(new_bill_number),
            customer_name=customer,
            from_date=first_date,
            to_date=last_date.date(),
            coolers=coolers_total,
            Rate=int(customer.rate),
            Amount=int(coolers_total) * int(customer.rate),
            Pending_amount=int(customer_account.due),
            Advanced_amount=int(0),
            Total=int(coolers_total) * int(customer.rate) + int(customer_account.due),
            addedby=request.user.username,
        )

        customer_account.due = int(coolers_total) * int(customer.rate) + int(customer_account.due)
        customer_account.save()

        customer_daily_entry.coolers = 0
        customer_daily_entry.save()

        return JsonResponse({"message": "Customer Bill Generated"}, status=status.HTTP_200_OK)

    return internal_server_error()
