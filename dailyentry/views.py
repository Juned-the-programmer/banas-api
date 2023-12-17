from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from django.db.models import Sum
import datetime
from datetime import time, timedelta, date

from .models import DailyEntry, pending_daily_entry
from customer.models import Customer, CustomerAccount
from .serializer import *
from banas.cache_conf import *

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

@api_view(['POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def verify_pending_daily_entry(request):
    if request.method == 'POST':
        serializers = DailyEntry_Verify_Result_Serializer(data=request.data, many=True)
        print(serializers)
        if serializers.is_valid():
            addedby = request.user.username
            daily_entries = []
            customer_data = customer_cached_data()

            for data_item in serializers.initial_data:
                customer_id = data_item.get("customer")
                cooler = data_item.get("cooler")
                pending_id = data_item.get("pending_id")

                customer_pending_daily_entry = pending_daily_entry.objects.get(id=pending_id).delete()

                customer_name = customer_data.get(id=cutomer_id)

                daily_entry_data = DailyEntry(
                    customer= customer_name,
                    cooler= cooler,
                    addedby= f'{customer_name.first_name} {customer_name.last_name}'
                )
                daily_entries.append(daily_entry_data)

            DailyEntry.objects.bulk_create(daily_entries)
            return JsonResponse({"message" : "Verified Successfully ! "}, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse({"message" : "Something went wrong, Please try again later ! "}, status=    status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_pending_daily_entry(request):
    if request.method == 'GET':
        daily_entry_pending = pending_daily_entry.objects.all()
        serializers = Pending_Daily_Entry_Serializer(daily_entry_pending, many=True)
        return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)