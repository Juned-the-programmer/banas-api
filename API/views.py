from django.shortcuts import render
from .models import *
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.response import Response
from django.http import JsonResponse
from django.core import serializers
from rest_framework import status
from .serializer import *
from datetime import date, timedelta
import datetime
import calendar
from django.db.models import Sum,Min,Max,Avg

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard(request):
    return JsonResponse("Dashboard" , safe=False)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_route(request):
    if request.method == 'POST':
        route_data = request.data
        route_serializer = RouteSerializer(data=route_data)

        if route_serializer.is_valid():
            route_serializer.save()
            return Response(route_serializer.data , status=status.HTTP_200_OK)

        return Response(route_serializer.errors , status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_customer(request):
    if request.method == 'POST':
        data = request.data
        data_values = list(data.values())
        pk = data_values[0]

        customer_data = {
            "name" : data_values[0],
            "route" : data_values[1],
            "rate" : data_values[2]
        }

        customer_serializer = CustomerSerializer(data=customer_data)
    
        if customer_serializer.is_valid():
            customer_serializer.save()
            customeraccount = CustomerAccount.objects.get(customer_name = Customer.objects.get(name=data_values[0]).id)
            customeraccount.due = data_values[3]
            customeraccount.save()
            
            return Response(customer_serializer.data , status=status.HTTP_200_OK)


        return Response(customer_serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
def list_route(request):
    if request.method == 'GET':
        routes = Route.objects.all()
        serializer = RouteSerializer(routes ,many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_customer(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers ,many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_daily_entry(request):
    today_date = datetime.datetime.now()
    year = today_date.year
    month = today_date.month
    day = today_date.day
    last_date = calendar.monthrange(year, month)[0]

    data = request.data
    data_values = list(data.values())
    pk = data_values[0]
    # print(list(data.keys()))

    if request.method == 'POST':
        serializer = DailyEntrySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            if day == last_date:
        
                customer_name = Customer.objects.get(pk=pk).id

                last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
                start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

                last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
                start_day = start_day_of_prev_month.strftime("%Y-%m-%d")


                total_cooler = DailyEntry.objects.filter(date__gte=start_day_of_prev_month , date__lte=last_day_of_prev_month).aggregate(Sum('cooler'))
                coolers_total = total_cooler['cooler__sum']
                
                if coolers_total == None:   
                    coolers_total = 0


                last_month_due_amount = CustomerAccount.objects.get(customer_name = pk).due
                rate = Customer.objects.get(pk=pk).rate

                total = (int(coolers_total) * int(rate)) + int(last_month_due_amount)

                bill_data = {
                    'customer_name' : pk ,
                    'to_date' : last_day ,
                    'from_date' : start_day ,
                    'coolers' : coolers_total ,
                    'Pending_amount' : last_month_due_amount ,
                    'Rate' : rate , 
                    'Total' : total
                }
                print(bill_data)
                data = bill_data
                data_values = list(data.values())
                pk = data_values[0]
                # print(list(data.keys()))

                bill_serializer = GenerateBillSerializer(data = bill_data)
                if bill_serializer.is_valid():
                    bill_serializer.save()
                    customer = CustomerAccount.objects.get(customer_name=pk)
                    customer.due = data_values[6]
                    customer.save()

            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_201_CREATED)
    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def daily_count(request):
    if request.method == 'GET':
        customer_count = DailyEntry.objects.distinct().filter(date=date.today()).count()
        
        coolers = DailyEntry.objects.distinct().filter(date=date.today()).aggregate(Sum('cooler'))
        coolers_total = coolers['cooler__sum']
        
        if coolers_total == None:   
            coolers_total = 0

        return JsonResponse({'customer_count' : customer_count , 'coolers_total' : coolers_total})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def customer_payment(request):
    if request.method == 'POST':
        serializer = CustomerPaymentSerializer(data = request.data)
        
        # Conver the data to the list to get the each and every element from that data
        data = request.data
        data_values = list(data.values())
        pk = data_values[0]
        print(list(data.keys()))
        # Ends here
        
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        if serializer.is_valid():
            serializer.save()
            customer = CustomerAccount.objects.get(customer_name = pk)
            customer.due = int(data_values[1]) - int(data_values[2])
            customer.save()
            
            customer_bill = CustomerBill.objects.filter(customer_name = pk).filter(paid=False).get(from_date=start_day)
            customer_bill.paid = True
            customer_bill.save()

            return Response(status=status.HTTP_201_CREATED)


        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def customer_account(request , pk):

    try:
        customer = CustomerAccount.objects.get(customer_name = pk)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CustomerAccountSerializer(customer , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def due_list(request,pk):
    if request.method == 'GET':

        try:
            route = Route.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response("Customer Route Not Found" , status=status.HTTP_404_NOT_FOUND)

        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        # customer_due = CustomerAccount.objects.filter(customer_name__id__in = Customer.objects.filter(route=pk))
        customer_due_list = CustomerBill.objects.filter(customer_name__id__in = Customer.objects.filter(route=pk)).filter(paid=False).filter(from_date=start_day)
        # serializer = CustomerAccountSerializer(customer_due ,many=True)
        serializer = GenerateBillSerializer(customer_due_list , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def due_customer(request , pk):
    if request.method == 'GET':
        try:
            customer = CustomerAccount.objects.get(customer_name=pk)
        except:
            return Response("Customer Not Found",status=status.HTTP_400_BAD_REQUEST)

        customer_due = customer.due
        return JsonResponse(customer_due , safe=False)
    return Response("Invalid Request",status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def customer_detail(request , pk):
    today_date = datetime.datetime.now()
    first_day_of_month = today_date.replace(day=1)

    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=pk)
        except:
            return Response("Customer Not Found",status=status.HTTP_400_BAD_REQUEST)

        customer_detail = customer
        detail_serializer = CustomerSerializer(customer_detail)
        
        customer_bills = CustomerBill.objects.filter(customer_name = customer.id)
        bill_serializer = GenerateBillSerializer(customer_bills , many=True)

        customer_daily_entry = DailyEntry.objects.filter(date__gte=first_day_of_month)
        daily_entry_serializer = DailyEntrySerializer(customer_daily_entry , many=True)

        return JsonResponse({
            'detail' : detail_serializer.data,
            'bills' : bill_serializer.data,
            'daily_entry' : daily_entry_serializer.data
        })

    return Response("Invalid Request",status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser()])
def bill_detail(request , pk):
    if request.method == 'GET':
        try:
            bill = CustomerBill.objects.get(pk=pk)
        except CustomerBill.DoesNotExist:
            return Response("Bill Not Found" , status=status.HTTP_400_BAD_REQUEST)

        customer_bill = GenerateBillSerializer(bill)
        daily_entry = DailyEntry.objects.filter(date__gte=bill.from_date , date__lte=bill.to_date)
        daily_entry_serializer = DailyEntrySerializer(daily_entry , many=True)

        return JsonResponse({
            'bill' : customer_bill.data,
            'daily_entry' : daily_entry_serializer.data
        })
    return Response("Invalid Request" , status=status.HTTP_400_BAD_REQUEST)