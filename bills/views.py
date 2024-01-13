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
  
from .models import CustomerBill
from .serializer import *
from exception.views import *

#create your view here
@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def bill_detail(request, pk):
  import pytz
  if request.method == 'GET':
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

    from_date_new = datetime.datetime(int(from_date_year) , int(from_date_month) , int(from_date_date), tzinfo=pytz.UTC)
    
    to_date_new = datetime.datetime(int(to_date_year) , int(to_date_month) , int(to_date_date),23,59,59, tzinfo=pytz.UTC)

    daily_entry = DailyEntry.objects.filter(date_added__gte=from_date_new, date_added__lte=to_date_new).filter(customer=bill.customer_name.id)
    daily_entry_serializer = DialyEntrySerializerGETDashboard(daily_entry, many=True)

    return JsonResponse({
      'bill': customer_bill.data,
      'daily_entry': daily_entry_serializer.data
    }, status=status.HTTP_200_OK)

  return internal_server_error()

@api_view(['POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def generate_bill(request, pk):
  if request.method == 'POST':
    try:
      customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
      return customer_not_found_exception(pk)
    
    #today date
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()
    
    customer_daily_entry = customer_daily_entry_monthly.objects.get(customer=pk)

    coolers_total = customer_daily_entry.coolers
    
    customer_account = CustomerAccount.objects.get(customer_name=pk)    
    
    CustomerBill.objects.create(
      customer_name=customer,
      from_date=first_date,
      to_date=last_date.date(),
      coolers=coolers_total,
      Rate=int(customer.rate),
      Amount=int(coolers_total) * int(customer.rate),
      Pending_amount=int(customer_account.due),
      Advanced_amount=int(0),
      Total=int(coolers_total) * int(customer.rate) + int(customer_account.due),
      addedby=request.user.username
    )
    
    customer_account.due = int(coolers_total) * int(customer.rate) + int(customer_account.due)
    customer_account.save()

    customer_daily_entry.coolers = 0
    customer_daily_entry.save()
    
    return JsonResponse({"message" : "Customer Bill Generated"}, status=status.HTTP_200_OK)
  
  return internal_server_error()