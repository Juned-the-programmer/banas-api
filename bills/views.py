from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from .serializer import *
from .models import CustomerBill
from django.http import JsonResponse
import datetime
from dailyentry.models import DailyEntry
from dailyentry.serializer import *

#create your view here

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def bill_detail(request, pk):
  import pytz
  if request.method == 'GET':
    try:
      bill = CustomerBill.objects.get(pk=pk)
    except CustomerBill.DoesNotExist:
      return JsonResponse({
        'message': "Bill Not Found"
      }, status=status.HTTP_400_BAD_REQUEST)

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

  return JsonResponse({
    'message': "Something went wrong"
  }, status=status.HTTP_400_BAD_REQUEST)