import datetime

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.core.cache import cache

from .models import *
from .serializer import *
from bills.models import CustomerBill
from bills.serializer import *
from dailyentry.models import DailyEntry, customer_daily_entry_monthly
from dailyentry.serializer import *
from payment.models import CustomerPayment
from payment.serializer import *
from banas.cache_conf import *
from exception.error_constant import *
from exception.views import *

# Create your views here.
''' To POST customer and get the complete list of all the customer from database 
Validation for POST has been done by the serializer by itself don't want to customize here.
'''
class CustomerListView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()

    def get_serializer_class(self):
        method = self.request.method
        if method == 'POST':
            return CustomerSerializer
            cache.delete("Customer")
            customer_cached_data()
        else:
            return CustomerSerializerList

    def perform_create(self, serializer):
        serializer.save(addedby=self.request.user.username)

    def list(self, request, *args, **kwargs):
        customer_data = customer_cached_data()
        customer_data_serializer = CustomerSerializerList(customer_data, many=True)
        return JsonResponse(customer_data_serializer.data , status = status.HTTP_200_OK, safe=False)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_customer_by_route(request, pk):
    if request.method == 'GET':
        customer_data = customer_cached_data()

        customer_route = customer_data.filter(route=pk).filter(active=True)
        customer_route_serializer = CustomerSerializerList(customer_route, many=True)

        return JsonResponse(
            customer_route_serializer.data
        , status = status.HTTP_200_OK, safe=False)
        
    return internal_server_error()

@api_view(['GET' , 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def Customer_detail_view_update(request , pk):
    try:
        customer_data = customer_cached_data()
        customer = customer_data.get(id=pk)
    except Customer.DoesNotExist:
        return customer_not_found_exception(pk)
            
    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return JsonResponse(serializer.data , status=status.HTTP_200_OK)
    
    if request.method == 'PUT':
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save(updatedby=request.user.username)
            cache.delete("Customer")
            customer_cached_data()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            return serializer_errors(serializer.errors)
            
    return internal_server_error()

@api_view(['PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def customer_account(request, pk):
    try:
        customer_data = customer_cached_data()
        customer_account = customer_data.CustomerAccount
        customer = customer_account.get(customer_name = pk)
    except Customer.DoesNotExist:
        return customer_not_found_exception(pk)

    if request.method == 'PUT':
        serializer = CustomerAccountSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save(updatedby=request.user.username)
            return JsonResponse(
            serializer.data
            , status=status.HTTP_201_CREATED)
        else:
            return serializer_errors(serializer.errors)
        
    return internal_server_error()

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def due_customer(request, pk):
    if request.method == 'GET':
        try:
            customer_data = customer_cached_data()
            customer = customer_data.get(id = pk).customer_account
        except Customer.DoesNotExist:
            return customer_not_found_exception(pk)
        
        customer_due = customer.due
        return JsonResponse({
            'customer_name': customer.customer_name.first_name + ' ' + customer.customer_name.last_name,
            'due': customer_due}, status=status.HTTP_200_OK)
    
    return internal_server_error()

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def customer_detail(request, pk):
    today_date = datetime.datetime.now()
    first_day_of_month = today_date.replace(day=1)

    if request.method == 'GET':
        try:
            customer_data = customer_cached_data()
            customer = customer_data.get(id = pk)
        except:
            return customer_not_found_exception(pk)

        customer_detail = customer
        detail_serializer = CustomerSerializerGET(customer_detail)

        customer_bills = customer.customer_bill.all()
        bill_serializer = DetailBillSerializer(customer_bills, many=True)

        customer_daily_entry = customer.customer_daily_entry.filter(date_added__gte=first_day_of_month).filter(customer=customer.id)
        daily_entry_serializer = DialyEntrySerializerGETDashboard(customer_daily_entry, many=True)

        customer_daily_entry_total = customer_daily_entry_monthly.objects.get(customer=customer.id).coolers

        customer_payment = customer.customer_payment.filter(customer_name=pk)
        payment_serializer = CustomerPaymentSerializerGET(customer_payment,many=True)

        total_customer_payment = customer.customer_payment.filter(customer_name=pk).aggregate(Sum("paid_amount"))
        total_payment = total_customer_payment['paid_amount__sum']

        due_payment = customer.customer_account.due

        if total_payment is None:
            total_payment = 0
        else:
            total_payment = total_payment

        return JsonResponse({
        'customer_detail': detail_serializer.data,
        'bills': bill_serializer.data,
        'daily_entry': daily_entry_serializer.data,
        'total_coolers': customer_daily_entry_total,
        'payments' : payment_serializer.data,
        'total_payments' : total_payment,
        'due_payments' : due_payment
        }, status=status.HTTP_200_OK)

    return internal_server_error()