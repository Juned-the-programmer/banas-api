from django.shortcuts import render
from .models import *
from rest_framework.decorators import api_view , permission_classes
from django.contrib.auth.models import User
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
from rest_framework_simplejwt.views import TokenObtainPairView
import json

# Create your views here.

class CustomTokenObtainPairView(TokenObtainPairView):

  serializer_class = CustomTokenObtainPairSerializer
  token_obtain_pair = TokenObtainPairView.as_view()

@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def dashboard(request):

    if request.method == 'GET':
        today_date = datetime.date.today()

        data_list = []

        for i in range(0,7):
            daily_entry = DailyEntry.objects.filter(date=today_date - timedelta(days=i)).aggregate(Sum('cooler'))
            coolers_total = daily_entry['cooler__sum']

            if coolers_total is None:
                coolers = 0
            else:
                coolers = coolers_total

            data_list.append({"date" : str(today_date - timedelta(days=i)) , "coolers" : coolers})

        return JsonResponse({
            'status': '200',
            'data' : data_list
        }, status = status.HTTP_200_OK)

    if request.method == 'POST':
        date_data = request.data
        data_values = list(date_data.values())

        #Configuring date
        from_date = datetime.datetime.strptime(data_values[0], "%Y-%m-%d")
        to_date = datetime.datetime.strptime(data_values[1], "%Y-%m-%d")
        days = to_date - from_date

        data_list = []

        for i in range(0,int(days.days)):
            daily_entry = DailyEntry.objects.filter(date=to_date - timedelta(days=i)).aggregate(Sum('cooler'))
            coolers_total = daily_entry['cooler__sum']

            if coolers_total is None:
                coolers = 0
            else:
                coolers = coolers_total

            data_list.append({"date" : str(to_date - timedelta(days=i)) , "coolers" : coolers})

        return JsonResponse({
            'status': '200',
            'data' : data_list
        }, status = status.HTTP_200_OK)

    return JsonResponse({
        'status': '400',
        'data' : "There is some error, Please try again!"
    }, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_profile(request):
    user = User.objects.get(username=request.user.username)

    return JsonResponse({
        'status' : 200,
        'username': user.username,
        'id': user.id,
        'first_name' : user.first_name,
        'last_name' : user.last_name,
        'full_name' : user.first_name + ' ' + user.last_name,
        'is_superuser' : user.is_superuser,
        'email' : user.email} , status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_route(request):
    if request.method == 'POST':
        route_data = request.data
        route_serializer = RouteSerializer(data=route_data)

        if route_serializer.is_valid():
            route_serializer.save(addedby=request.user.username)
            
            return JsonResponse({
                'status' : 200,
                'data' : route_serializer.data} , status=status.HTTP_200_OK)

        return JsonResponse({
            'status' : 400,
            'data': route_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_route(request,pk):
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return JsonResponse({
            'status' : 400,
            'data' : "Route Not Found"
        },status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        serializer = RouteSerializer(route , data=request.data)
        if serializer.is_valid():
            serializer.save(updatedby=request.user.username)
            return JsonResponse({
                'status' : 200,
                'data' : serializer.data
            }, status=status.HTTP_200_OK)

    return JsonResponse({
        'status' : 400,
        'data' : serializer.errors
    } ,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_route(request):
    if request.method == 'GET':
        routes = Route.objects.all()
        serializer = RouteSerializer(routes ,many=True)
        return JsonResponse({
            'status' : 200,
            'data' : serializer.data} , status=status.HTTP_200_OK)

    return JsonResponse({
        'status' : 400,
        'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

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
            customer_serializer.save(addedby=request.user.username)
            if(len(data_values) > 3):
                customeraccount = CustomerAccount.objects.get(customer_name = Customer.objects.get(name=data_values[0]).id)
                customeraccount.due = data_values[3]
                customeraccount.updatedby = request.user.username
                customeraccount.save()
            
            return JsonResponse({
                'status' : 201,
                'data' : customer_serializer.data} , status=status.HTTP_201_CREATED)


        return JsonResponse({
            'status' : 400,
            'data' : customer_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

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
            serializer.save(updatedby=request.user.username)
            return JsonResponse({
                'status' : 201,
                'data' : serializer.data} , status=status.HTTP_201_CREATED)
        
        return JsonResponse({
            'status' : 400,
            'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_customer(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializerGET(customers ,many=True)
        return JsonResponse({
            'status' : 200,
            'data' : serializer.data} , status=status.HTTP_200_OK)

    return JsonResponse({
        'status' : 400,
        'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_customer_detail(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return JsonResponse({
            'status' : 404,
            'data' : "Customer Not Found"
        } , status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        customer = Customer.objects.get(pk=pk)
        serializer = CustomerSerializerGET(customer)
        return JsonResponse({
            'status' : 200,
            'data' : serializer.data} , status=status.HTTP_200_OK)
    
    return JsonResponse({
        'status' : 400,
        'data' : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
            serializer.save(addedby=request.user.username)

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
                    bill_serializer.save(addedby=request.user.username)
                    customer = CustomerAccount.objects.get(customer_name=pk)
                    customer.due = data_values[6]
                    customer.updatedby = request.user.username
                    customer.save()

            return JsonResponse({
                'status' : 201,
                'data' : serializer.data},status=status.HTTP_201_CREATED)

        return JsonResponse({
            'status' : 201,
            'data' : serializer.data} , status=HTTP_201_CREATED)

    return JsonResponse({
        'status' : 400,
        'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def daily_count(request):
    if request.method == 'GET':
        customer_count = DailyEntry.objects.distinct().filter(date=date.today()).count()
        
        coolers = DailyEntry.objects.distinct().filter(date=date.today()).aggregate(Sum('cooler'))
        coolers_total = coolers['cooler__sum']
        
        if coolers_total == None:   
            coolers_total = 0

        return JsonResponse({'status' : 200 , 'customer_count' : customer_count , 'coolers_total' : coolers_total}, status=status.HTTP_200_OK)

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
            serializer.save(addedby=request.user.username)
            try:
                customer_data = Customer.objects.filter(route = Route.objects.get(id = data_values[1])).get(id = pk).id
                customer = CustomerAccount.objects.get(customer_name = customer_data)
                customer.due = int(customer.due) - int(data_values[2])
                customer.updatedby = request.user.username
                customer.save()
                
                customer_bill = CustomerBill.objects.filter(customer_name = pk).filter(paid=False).get(from_date=start_day)
                customer_bill.paid = True
                customer_bill.updatedby = request.user.username
                customer_bill.save()
            except:
                return JsonResponse({
                    'status' : 400,
                    'detail' : "Customer is not this route"
                },status = status.HTTP_400_BAD_REQUEST)

            return JsonResponse({
                'status' : 200,
                'detail' : "Bill Paid and Customer Account Updated"
            } , status=status.HTTP_201_CREATED)


        return Response({
            'status' : 400,
            'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def customer_account(request , pk):

    try:
        customer = CustomerAccount.objects.get(customer_name = pk)
    except Customer.DoesNotExist:
        return JsonResponse({
            'status' : 400,
            'data' : "Customer Not Found"
        },status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CustomerAccountSerializer(customer , data = request.data)
        if serializer.is_valid():
            serializer.save(updatedby=request.user.username)
            return JsonResponse({
                'status' : 200,
                'data' : serializer.data
            }, status=status.HTTP_201_CREATED)

        return JsonResponse({
            'status' : 400,
            'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def due_list_route(request,pk):
    if request.method == 'GET':

        try:
            route = Route.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return JsonResponse({
                'status' : 400,
                'data' : "Route Not Found"
            } , status=status.HTTP_404_NOT_FOUND)

        customer_due_list = CustomerAccount.objects.filter(customer_name__id__in = Customer.objects.filter(route=pk))
        serializer = CustomerAccountSerializerGET(customer_due_list , many=True)

        customer_due_list_filter = CustomerAccount.objects.filter(customer_name__id__in = Customer.objects.filter(route=pk)).aggregate(Sum('due'))
        customer_due_list_total = customer_due_list_filter['due__sum']

        return JsonResponse({
            'status' : 200,
            'duelist_data' : serializer.data ,
            'due_total' : customer_due_list_total} , status=status.HTTP_200_OK)

    return Response({
        'status' : 400,
        'data' : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def due_list(request):
    if request.method == 'GET':

        customerdue = CustomerAccount.objects.all()
        serializer = CustomerAccountSerializerGET(customerdue , many=True)

        customer_due_list = CustomerAccount.objects.all().aggregate(Sum('due'))
        customer_due_list_total = customer_due_list['due__sum']

        return JsonResponse({
            'status' : 200,
            'duelist_data' : serializer.data,
            'due_total' : customer_due_list_total
        } , status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def due_customer(request , pk):
    if request.method == 'GET':
        try:
            customer = CustomerAccount.objects.get(customer_name=pk)
        except:
            return JsonResponse({
                'status' : 400,
                'data' : "Customer Not Found"
            }, status=status.HTTP_400_BAD_REQUEST)

        customer_due = customer.due
        return JsonResponse({
            'status' : 200,
            'customer_name' : customer.customer_name.name,
            'due' : customer_due} , status=status.HTTP_200_OK)

    return JsonResponse({
        'status' : 400,
        'data' : "Something went wrong"
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def customer_detail(request , pk):
    today_date = datetime.datetime.now()
    first_day_of_month = today_date.replace(day=1)

    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=pk)
        except:
            return JsonResponse({
                'status' : 400,
                'data' : "Customer Not Found"
            }, status=status.HTTP_400_BAD_REQUEST)

        customer_detail = customer
        detail_serializer = CustomerSerializerGET(customer_detail)
        
        customer_bills = CustomerBill.objects.filter(customer_name = customer.id)
        bill_serializer = DetailBillSerializer(customer_bills , many=True)

        customer_daily_entry = DailyEntry.objects.filter(date__gte=first_day_of_month).filter(customer_name=customer.id)
        daily_entry_serializer = DialyEntrySerializerGETDashboard(customer_daily_entry , many=True)

        return JsonResponse({
            'status' : 200,
            'customer_detail' : detail_serializer.data,
            'bills' : bill_serializer.data,
            'daily_entry' : daily_entry_serializer.data
        }, status=status.HTTP_200_OK)

    return JsonResponse({
        'status' : 400,
        'data' : "Something Went Wrong"
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def bill_detail(request , pk):
    if request.method == 'GET':
        try:
            bill = CustomerBill.objects.get(pk=pk)
        except CustomerBill.DoesNotExist:
            return JsonResponse({
                'status' : 400,
                'data' : "Bill Not Found"
            } , status=status.HTTP_400_BAD_REQUEST)

        customer_bill = GenerateBillSerializerGET(bill)
        customer_name = CustomerBill.objects.get(pk=pk).id

        daily_entry = DailyEntry.objects.filter(date__gte=bill.from_date , date__lte=bill.to_date).filter(customer_name = customer_name)
        daily_entry_serializer = DailyEntrySerializer(daily_entry , many=True)

        return JsonResponse({
            'status' : 200,
            'bill' : customer_bill.data,
            'daily_entry' : daily_entry_serializer.data
        }, status=status.HTTP_200_OK)

    return JsonResponse({
        'status' : 400,
        'data' : "Something went wrong"
    } , status=status.HTTP_400_BAD_REQUEST)