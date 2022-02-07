from django.shortcuts import render
from .models import *

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.core import serializers
from rest_framework import status

from .serializer import *
from datetime import date, timedelta

from django.db.models import Sum,Min,Max,Avg
# Create your views here.
@api_view(['GET'])
def login(request):
    return JsonResponse("Login Page" , safe=False)

@api_view(['GET'])
def dashboard(request):
    return JsonResponse("Dashboard" , safe=False)

@api_view(['POST'])
def add_route(request):
    if request.method == 'POST':
        route_data = request.data
        route_serializer = RouteSerializer(data=route_data)

        if route_serializer.is_valid():
            route_serializer.save()
            return Response(route_serializer.data , status=status.HTTP_200_OK)

        return Response(route_serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_customer(request):
    if request.method == 'POST':
        customer_data = request.data
        customer_serializer = CustomerSerializer(data=customer_data)

        if customer_serializer.is_valid():
            customer_serializer.save()
            return Response(customer_serializer.data , status=status.HTTP_200_OK)

        return Response(customer_serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_customer(request,pk):
    
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CustomerSerializer(customer , data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_route(request):
    if request.method == 'GET':
        routes = Route.objects.all()
        serializer = RouteSerializer(routes ,many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_customer(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers ,many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_daily_entry(request):
    if request.method == 'POST':
        serializer = DailyEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def daily_count(request):
    if request.method == 'GET':
        customer_count = DailyEntry.objects.distinct().filter(date=date.today()).count()
        
        coolers = DailyEntry.objects.distinct().filter(date=date.today()).aggregate(Sum('cooler'))
        coolers_total = coolers['cooler__sum']
        
        if coolers_total == None:   
            coolers_total = 0

        return JsonResponse({'customer_count' : customer_count , 'coolers_total' : coolers_total})

@api_view(['POST'])
def customer_payment(request):
    if request.method == 'POST':
        serializer = CustomerPaymentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def customer_account(request , pk):

    try:
        customer = CustomerAccount.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CustomerAccountSerializer(customer , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def due_list(request,pk):
    if request.method == 'GET':

        try:
            customer = CustomerAccount.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response("Customer Route Not Found" , status=status.HTTP_404_NOT_FOUND)

        customer_due = CustomerAccount.objects.filter(customer_name__id__in = Customer.objects.filter(route=pk))
        serializer = CustomerAccountSerializer(customer_due ,many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_bill_data(request , pk):

    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        customer_name = Customer.objects.get(pk=pk).name

        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        total_cooler = DailyEntry.objects.filter(date__gte=start_day_of_prev_month , date__lte=last_day_of_prev_month).aggregate(Sum('cooler'))
        coolers_total = total_cooler['cooler__sum']
        
        if coolers_total == None:   
            coolers_total = 0

        print(coolers_total)

        last_month_due_amount = CustomerAccount.objects.get(customer_name = pk).due
        rate = Customer.objects.get(pk=pk).rate

        total = ( int(coolers_total) * int(rate) ) + int(last_month_due_amount)

        return JsonResponse(
            {'customer_name' : customer_name ,
             'last_day' : last_day_of_prev_month ,
             'start_day' : start_day_of_prev_month ,
             'coolers' : coolers_total ,
             'due_amount' : last_month_due_amount ,
             'rate' : rate , 
             'total' : total}
        )

@api_view(['POST'])
def generate_bill(request):
    if request.method == 'POST':
        serializer = GenerateBillSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)