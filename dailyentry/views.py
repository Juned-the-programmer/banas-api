from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from django.db.models import Sum
import datetime
from datetime import time, timedelta, date
from django.utils import timezone
from django.db import connection

from .models import DailyEntry, pending_daily_entry, customer_qr_code, pending_daily_entry, DailyEntry_dashboard
from customer.models import Customer, CustomerAccount
from .serializer import *
from banas.cache_conf import *
from exception.views import *

# Create your views here.

@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry(request):
    if request.method == 'GET':
        today_date = datetime.datetime.now()
        
        dailyEntry = DailyEntry.objects.filter(date_added__date=today_date.date())
        serializer = DailyEntrySerializerGET(dailyEntry, many=True)
        return JsonResponse(
        serializer.data, status=status.HTTP_200_OK, safe=False)

    if request.method == 'POST':
        serializer = DailyEntrySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(addedby=request.user.username)
            serializer.save(date_added=timezone.now())

            return JsonResponse(
                serializer.data , status=status.HTTP_201_CREATED)
        else:
            return serializer_errors(serializer.errors)
    
    return internal_server_error()

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry_count(request):
    if request.method == 'GET':
        dashboard_detail = DailyEntry_dashboard.objects.first()

        today_coolers_total = dashboard_detail.coolers_count
        today_customer_count = dashboard_detail.customer_count

        return JsonResponse({
        'today_customer_count': today_customer_count,
        'today_coolers_total': today_coolers_total}, status=status.HTTP_200_OK)

    return internal_server_error()
    
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
        return daily_entry_not_found(pk)

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

            return serializer_errors(serializer.errors)
        
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
                    addedby=addedby,
                    date_added=timezone.now()
                )
                daily_entries.append(daily_entry_data)
                
            DailyEntry.objects.bulk_create(daily_entries)
            return JsonResponse({"message" : "Bulk Import success ! "}, status=status.HTTP_200_OK, safe=False)
        else:
            return serializer_errors(serializer.errors)
                        
    return internal_server_error()

@api_view(['POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def verify_pending_daily_entry(request):
    if request.method == 'POST':
        serializers = DailyEntry_Verify_Result_Serializer(data=request.data, many=True)
        if serializers.is_valid():
            addedby = request.user.username
            daily_entries = []
            customer_data = customer_cached_data()

            for data_item in serializers.initial_data:
                customer_id = data_item.get("customer")
                cooler = data_item.get("cooler")
                pending_id = data_item.get("pending_id")
                date_added = data_item.get("date_added")

                customer_pending_daily_entry = pending_daily_entry.objects.get(id=pending_id).delete()

                customer_name = customer_data.get(id=customer_id)

                daily_entry_data = DailyEntry(
                    customer= customer_name,
                    cooler= cooler,
                    addedby= f'{customer_name.first_name} {customer_name.last_name}',
                    date_added=date_added
                )
                daily_entries.append(daily_entry_data)

            batch_size = len(daily_entries)
            DailyEntry.objects.bulk_create(daily_entries, batch_size=batch_size)
            return JsonResponse({"message" : "Verified Successfully ! "}, status=status.HTTP_200_OK, safe=False)
        else:
            return serializer_errors(serializers.errors)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_pending_daily_entry(request):
    if request.method == 'GET':
        daily_entry_pending = pending_daily_entry.objects.all()
        serializers = Pending_Daily_Entry_Serializer(daily_entry_pending, many=True)
        return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)

def customer_qr_daily_entry(request,pk):
    if request.method == 'POST':

        qr_code_pin = customer_qr_code.objects.get(customer=pk).qrcode_pin

        if (qr_code_pin == int(request.POST['pin'])):
            pending_daily_entry_customer = pending_daily_entry(
                customer = Customer.objects.get(id=pk),
                coolers = int(request.POST['coolers'])
            )
            pending_daily_entry_customer.save()

    current_date_time = datetime.datetime.now().time()
    target_start_date_time = time(9,0,0)
    target_end_date_time = time(18,0,0)

    if (current_date_time > target_start_date_time and current_date_time < target_end_date_time):
        return render(request, 'dailyentry/dailyentry.html')
    else:
        return render(request, 'dailyentry/dailyentrytime.html')


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def historical_data_retriever(request):
    if request.method == 'GET':
        params = request.GET.get('historical')
        
        # response_data = []

        # for param in params:
        table_name = f"dailyentry_{params}"

        # Check if the table exists
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT to_regclass('{table_name}')")
            if not cursor.fetchone()[0]:
                return JsonResponse({'error': 'Table not found'}, status=404)

        # Fetch data from the historical table
        query = f"SELECT * FROM {table_name}"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        # Convert the data to a list of dictionaries
        old_data = [dict(zip(columns, row)) for row in rows]

        old_data = DialyEntrySerializerGETDashboard(old_data, many=True)
        # response_data.append({
        #     'historical_month' : param,
        #     'data' : old_data.data
        # })

        return JsonResponse({
            f"historical_{params}" : old_data.data
        } , status=status.HTTP_200_OK, safe=False)

    return internal_server_error()