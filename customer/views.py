import datetime

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

from .models import *
from .serializer import *
from bills.models import CustomerBill
from bills.serializer import *
from dailyentry.models import DailyEntry
from dailyentry.serializer import *
from payment.models import CustomerPayment
from payment.serializer import *

# Create your views here.
class CustomerListView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()

    def get_serializer_class(self):
        method = self.request.method
        if method == 'POST':
            return CustomerSerializer
        else:
            return CustomerSerializerList

    def perform_create(self, serializer):
        serializer.save(addedby=self.request.user.username)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_customer_by_route(request, pk):
    if request.method == 'GET':
        customer_route = Customer.objects.filter(route=pk).filter(active=True)
        customer_route_serializer = CustomerSerializerGET(customer_route, many=True)

        return JsonResponse(
            customer_route_serializer.data
        , status = status.HTTP_200_OK, safe=False)
        
    return JsonResponse({
        "message" : "Something went wrong, Please try again ! "
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET' , 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def Customer_detail_view_update(request , pk):
    try:
        customer = Customer.objects.get(id=pk)
    except Customer.DoesNotExist:
        return JsonResponse({
            "message" : "Customer Doesn't Exists ! "}, 
            status=status.HTTP_404_NOT_FOUND)
            
    if request.method == 'GET':
        try:
            serializer = CustomerSerializer(customer)
            return JsonResponse(serializer.data , status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return JsonResponse({
            "message" : serializer.errors
            }, status = status.HTTP_400_BAD_REQUEST) 
    
    if request.method == 'PUT':
        try:
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save(updatedby=request.user.username)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
                
        except Customer.DoesNotExist:
            return JsonResponse({
                "message" : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    return JsonResponse({
        "message" : "Something went wrong, Please try again !"
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def customer_account(request, pk):
    try:
        customer = CustomerAccount.objects.get(customer_name=pk)
    except Customer.DoesNotExist:
        return JsonResponse({
        'data': "Customer Not Found"
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CustomerAccountSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save(updatedby=request.user.username)
            return JsonResponse(
            serializer.data
            , status=status.HTTP_201_CREATED)
        
        return JsonResponse({
            'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    return JsonResponse({
        "message" : "Something went wrong, Please try again ! "
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def due_customer(request, pk):
    if request.method == 'GET':
        try:
            customer = CustomerAccount.objects.get(customer_name=pk)
        except:
            return JsonResponse({
            'message': "Customer Not Found"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer_due = customer.due
        return JsonResponse({
            'customer_name': customer.customer_name.name,
            'due': customer_due}, status=status.HTTP_200_OK)
    
    return JsonResponse({
    'message': "Something went wrong"
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def customer_detail(request, pk):
    today_date = datetime.datetime.now()
    first_day_of_month = today_date.replace(day=1)

    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=pk)
        except:
            return JsonResponse({
                'message': "Customer Not Found"
            }, status=status.HTTP_400_BAD_REQUEST)

        customer_detail = customer
        detail_serializer = CustomerSerializerGET(customer_detail)

        customer_bills = CustomerBill.objects.filter(customer_name=customer.id)
        bill_serializer = DetailBillSerializer(customer_bills, many=True)

        customer_daily_entry = DailyEntry.objects.filter(date_added__gte=first_day_of_month).filter(customer=customer.id)
        daily_entry_serializer = DialyEntrySerializerGETDashboard(customer_daily_entry, many=True)

        customer_daily_entry_total = DailyEntry.objects.filter(date_added__gte=first_day_of_month).filter(
        customer=customer.id).aggregate(Sum("cooler"))
        total_coolers = customer_daily_entry_total['cooler__sum']

        customer_payment = CustomerPayment.objects.filter(customer_name=pk)
        payment_serializer = CustomerPaymentSerializerGET(customer_payment,many=True)

        total_customer_payment = CustomerPayment.objects.filter(customer_name=pk).aggregate(Sum("paid_amount"))
        total_payment = total_customer_payment['paid_amount__sum']

        due_payment = CustomerAccount.objects.get(customer_name=pk)
        due_serializer = CustomerAccountSerializer(due_payment)

        if total_payment is None:
            total_payment = 0
        else:
            total_payment = total_payment

        if total_coolers is None:
            total = 0
        else:
            total = total_coolers

        return JsonResponse({
        'customer_detail': detail_serializer.data,
        'bills': bill_serializer.data,
        'daily_entry': daily_entry_serializer.data,
        'total_coolers': total,
        'payments' : payment_serializer.data,
        'total_payments' : total_payment,
        'due_payments' : due_serializer.data
        }, status=status.HTTP_200_OK)

    return JsonResponse({
        'message': "Something Went Wrong"
    }, status=status.HTTP_400_BAD_REQUEST)