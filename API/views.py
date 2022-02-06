from django.shortcuts import render
from .models import *

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.core import serializers
from rest_framework import status

from .serializer import *
from datetime import date

from django.db.models import Sum,Min,Max,Avg
# Create your views here.
@api_view(['GET'])
def login(request):
    return JsonResponse("Login Page" , safe=False)

@api_view(['POST'])
def add_route(request):
    if request.method == 'POST':
        route_data = request.data
        route_serializer = RouteSerializer(data=route_data)

        if route_serializer.is_valid():
            route_serializer.save()
            return Response(route_serializer.data)

        return Response(route_serializer.errors)

@api_view(['POST'])
def add_customer(request):
    if request.method == 'POST':
        customer_data = request.data
        customer_serializer = CustomerSerializer(data=customer_data)

        if customer_serializer.is_valid():
            customer_serializer.save()
            return Response(customer_serializer.data)

        return Response(customer_serializer.errors)

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
        # routes = Route.objects.values('route_name')
        routes = Route.objects.all()
        serializer = RouteSerializer(routes ,many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)


@api_view(['GET'])
def list_customer(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers ,many=True)
        return Response(serializer.data)

@api_view(['GET'])
def Customer_Count(request):
    if request.method == 'GET':
        customer_count = Customer.objects.all().count()
        return JsonResponse(customer_count , safe=False)

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
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CustomerAccountSerializer(customer , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def customer_account_due(request):
