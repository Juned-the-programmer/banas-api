from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from django.db.models import Sum
import datetime
from datetime import time, timedelta, date

from .models import DailyEntry
from customer.models import Customer, CustomerAccount
from .serializer import *

# Create your views here.

@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry(request):
    if request.method == 'GET':
        dailyEntry = DailyEntry.objects.all()
        serializer = DailyEntrySerializerGET(dailyEntry, many=True)
        return JsonResponse(
        serializer.data, status=status.HTTP_200_OK, safe=False)

    if request.method == 'POST':
        serializer = DailyEntrySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(addedby=request.user.username)
            serializer.save(customer=Customer.objects.get(pk=pk))
            print("Serializer Saved") 

        return JsonResponse(
            serializer.data , status=status.HTTP_201_CREATED)
    
    return JsonResponse({
        "message" : serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry_count(request):
    if request.method == 'GET':
        now = date.today()
        month = now.month
        year = now.year
        day = now.day

        customer_count = DailyEntry.objects.distinct().filter(date_added__day=day , date_added__month=month, date_added__year=year).count()

        coolers = DailyEntry.objects.distinct().filter(date_added__day=day, date_added__month=month, date_added__year=year).aggregate(Sum('cooler'))
        coolers_total = coolers['cooler__sum']

        today_coolers = DailyEntry.objects.filter(date_added__day=day, date_added__month=month, date_added__year=year)
        today_coolers_serializer = DailyEntrySerializerGET(today_coolers, many=True)

        if coolers_total is None:
            total = 0
        else:
            total = coolers_total

        return JsonResponse({
        'today_coolers': today_coolers_serializer.data,
        'today_customer_count': customer_count,
        'today_coolers_total': total}, status=status.HTTP_200_OK)

    return JsonResponse({
        'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def view_delete_daily_entry(request, pk):
  
    #today date
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)
    # print(last_date.date())

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()
    # print(first_date)

    #Validating daily entry records
    try:
        dailyEntry = DailyEntry.objects.get(pk=pk)
    except DailyEntry.DoesNotExist:
        return JsonResponse({
        'message': 'Daily Entry Not Found !'}, status=status.HTTP_404_NOT_FOUND)

    # Deleting daily Entry
    if request.method == 'DELETE':
        if(DailyEntry.objects.filter(id=pk).filter(date_added__gte=first_date , date_added__lte=last_date)):
            if(DailyEntry.objects.filter(pk=pk).filter(date_added = last_date.date())):
                bill_detail = CustomerBill.objects.get(from_date = first_date, to_date = last_date.date(), customer_name = DailyEntry.objects.get(id=pk).customer)

                daily_entry_delete = DailyEntry.objects.get(pk=pk)
                daily_entry_cooler = DailyEntry.objects.get(pk=pk).cooler

                daily_entry_total = DailyEntry.objects.filter(date_added__gte=first_date, date_added__lte=last_date).filter(customer = DailyEntry.objects.get(id=pk).customer).aggregate(Sum('cooler'))
                total_coolers = daily_entry_total['cooler__sum']

                if total_coolers is None:
                    total_coolers = 0
                else:
                    total_coolers = int(total_coolers) - int(daily_entry_cooler)

                total_amount = (int(bill_detail.Rate) * int(total_coolers)) + int(bill_detail.Pending_amount) - int(bill_detail.Advanced_amount)

                due_amount = CustomerAccount.objects.get(customer_name=bill_detail.customer_name)
                due_amount.due = total_amount
                due_amount.save()
                
                bill_detail.coolers = total_coolers
                bill_detail.Amount = int(total_coolers) * int(bill_detail.Rate)
                bill_detail.Total = total_amount
                bill_detail.updatedby = request.user.username
                bill_detail.save()

                daily_entry_delete.delete()

                return JsonResponse({
                'message' : 'Daily Entry Deleted and Bill Updated successfully'
                } , status=status.HTTP_200_OK)

            else:
                dailyEntry = DailyEntry.objects.get(pk=pk)
                dailyEntry.delete()
                return JsonResponse({
                'message': 'DailyEntry deleted successfully'}, status=status.HTTP_200_OK)

        else:
            return JsonResponse({
                'message' : 'You cannot delete this record for more information contact admin'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    #Updating daily Entry
    if request.method == 'PUT':
        serializer = DailyEntrySerializer(dailyEntry, data=request.data)

        if(DailyEntry.objects.filter(id=pk).filter(date_added__gte=first_date , date_added__lte=last_date)):
            if(DailyEntry.objects.filter(pk=pk).filter(date_added = last_date.date())):
                bill_detail = CustomerBill.objects.get(from_date = first_date, to_date = last_date.date(), customer_name = DailyEntry.objects.get(id=pk).customer)

                if serializer.is_valid():
                    serializer.save(updatedby=request.user.username)

                daily_entry_total = DailyEntry.objects.filter(date_added__gte=first_date, date_added__lte=last_date).filter(customer = DailyEntry.objects.get(id=pk).customer).aggregate(Sum('cooler'))
                total_coolers = daily_entry_total['cooler__sum']

                if total_coolers is None:
                    total_coolers = 0
                else:
                    total_coolers = int(total_coolers)

                total_amount = (int(bill_detail.Rate) * int(total_coolers)) + int(bill_detail.Pending_amount) - int(bill_detail.Advanced_amount)

                due_amount = CustomerAccount.objects.get(customer_name=bill_detail.customer_name)
                due_amount.due = total_amount
                due_amount.save()
                
                bill_detail.coolers = total_coolers
                bill_detail.Amount = int(total_coolers) * int(bill_detail.Rate)
                bill_detail.Total = total_amount
                bill_detail.updatedby = request.user.username
                bill_detail.save()

                return JsonResponse({
                'message' : 'Daily Entry and Bill Updated successfully'
                } , status=status.HTTP_200_OK)

            else:
                if serializer.is_valid():
                    serializer.save(updatedby=request.user.username)
                    return JsonResponse(
                    serializer.data , status=status.HTTP_201_CREATED)

            return JsonResponse({
            'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return JsonResponse({
            'message' : "You cannot edit this record. For more Information contact admin"
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    #Getting Daily Entry
    if request.method == 'GET':
        dailyEntry = DailyEntry.objects.get(pk=pk)
        serializer = DailyEntrySerializerGETSingle(dailyEntry)
        return JsonResponse(
        serializer.data, status=status.HTTP_200_OK)

    return JsonResponse({
        'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry_bulk(request):
    print("dailyentry Bulk")
    if request.method == 'POST':
        serializer = DailyEntryBulkImportSerializer(data=request.data, many=True)
        if serializer.is_valid():
            addedby = request.user.username
            daily_entries = []
            
            for data_item in serializer.validated_data:
                customer_id = data_item['customer']
                cooler = data_item['cooler']
                
                daily_entry_data = DailyEntry(
                    customer= customer_id,
                    cooler= cooler,
                    addedby=addedby
                )
                daily_entries.append(daily_entry_data)
                
            DailyEntry.objects.bulk_create(daily_entries)
            return JsonResponse({"message" : "Bulk Import success ! "}, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)
                        
    return JsonResponse({"message" : "Something went wrong, Please try again later ! "}, status=status.HTTP_400_BAD_REQUEST)