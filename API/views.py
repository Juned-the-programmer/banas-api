import datetime
from datetime import date, timedelta
from django.utils import timezone

from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializer
from .serializer import *


# Create your views here.

class CustomTokenObtainPairView(TokenObtainPairView):
  serializer_class = CustomTokenObtainPairSerializer
  token_obtain_pair = TokenObtainPairView.as_view()


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def dashboard(request):
  if request.method == 'GET':
    today_date = datetime.date.today()

    data_list = []

    for i in range(0, 7):
      daily_entry = DailyEntry.objects.filter(date_added=today_date - timedelta(days=i)).aggregate(Sum('cooler'))
      coolers_total = daily_entry['cooler__sum']

      if coolers_total is None:
        coolers = 0
      else:
        coolers = coolers_total

      data_list.append({"date": str(today_date - timedelta(days=i)), "coolers": coolers})

    return JsonResponse(
        data_list
    , status=status.HTTP_200_OK , safe=False)

  if request.method == 'POST':
    date_data = request.data
    data_values = list(date_data.values())

    try:
      # Configuring date
      from_date = datetime.datetime.strptime(data_values[0], "%Y-%m-%d")
      to_date = datetime.datetime.strptime(data_values[1], "%Y-%m-%d")
      days = to_date - from_date

      data_list = []

      for i in range(0, int(days.days)):
        daily_entry = DailyEntry.objects.filter(date_added=to_date - timedelta(days=i)).aggregate(Sum('cooler'))
        coolers_total = daily_entry['cooler__sum']

        if coolers_total is None:
          coolers = 0
        else:
          coolers = coolers_total

        data_list.append({"date": str(to_date - timedelta(days=i)), "coolers": coolers})

      return JsonResponse(
        data_list
      , status=status.HTTP_200_OK, safe=False)
  
    except:
      return JsonResponse({
        'message': "Something went wrong, Please try again!"
      }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def get_profile(request):
  user = User.objects.get(username=request.user.username)

  return JsonResponse({
    'username': user.username,
    'id': user.id,
    'first_name': user.first_name,
    'last_name': user.last_name,
    'full_name': user.first_name + ' ' + user.last_name,
    'is_superuser': user.is_superuser,
    'email': user.email}, status=status.HTTP_200_OK)

@api_view(['GET' , 'POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def RouteListView(request):
  if request.method == 'POST':
    serializer = RouteSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save(addedby = request.user.username)
      return JsonResponse(serializer.data , status=status.HTTP_201_CREATED)

  if request.method == 'GET':
    route = Route.objects.all()
    serializer = RouteSerializer(route , many=True)
    
    return JsonResponse(serializer.data , status=status.HTTP_200_OK , safe=False)

  return JsonResponse({
    'message' : "Something went wrong, Please try again ! "
  }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET' , 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_update_route(request, pk):
  if request.method == 'GET':
    try:
      route = Route.objects.get(id=pk)
      route_serializer = RouteSerializer(route)
      return JsonResponse(route_serializer.data)
    except Route.DoesNotExist:
      return JsonResponse({
        'message' : "Route is not valid, Check once again ! "
      }, status=status.HTTP_404_NOT_FOUND)

  if request.method == 'PUT':
    try:
      route = Route.objects.get(id=pk)
      serializer = RouteSerializer(route , data=request.data)
      if serializer.is_valid():
        serializer.save(updatedby = request.user.username)
        return JsonResponse(serializer.data , status=status.HTTP_200_OK)

    except Route.DoesNotExist:
      return JsonResponse({
        'message' : "Route Doesn't Exists !"
      }, status=status.HTTP_400_BAD_REQUEST)

  return JsonResponse({
    'message' : "Something went wrong, Please try again later"
  }, status = status.HTTP_400_BAD_REQUEST)

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


# class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
#   queryset = Customer.objects.all()

#   def get_serializer_class(self):
#     method = self.request.method
#     if request.method == 'PUT':
#       return CustomerSerializer
#     else:
#       return CustomerSerializerList

#   def perform_update(self, serializer):
#     serializer.save(updatedby=self.request.user.username)

@api_view(['GET' , 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def Customer_detail_view_update(request , pk):
  if request.method == 'GET':
    customer = Customer.objects.get(id=pk)
    serializer = CustomerSerializer(customer)
    return JsonResponse(serializer.data , status=status.HTTP_200_OK)

  if request.method == 'PUT':
    try:
      customer = Customer.objects.get(id=pk)
      serializer = CustomerSerializer(customer , data=request.data)
      if serializer.is_valid():
        serializer.save(updatedby = request.user.username)      
        return JsonResponse(serializer.data , status=status.HTTP_200_OK)

    except Customer.DoesNotExist:
      return JsonResponse({
        "message" : "Customer Doesn't Exists ! " 
      }, status=status.HTTP_404_NOT_FOUND)

  return JsonResponse({
    "message" : "Something went wrong, Please try again ! "
  }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_customer_by_route(request, pk):
  if request.method == 'GET':
    customer_route = Customer.objects.filter(route=pk).filter(active=True)
    customer_route_serializer = CustomerSerializerGET(customer_route, many=True)

    return JsonResponse(
        customer_route_serializer.data
    , status = status.HTTP_200_OK, safe=False)

@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry_count(request):
  if request.method == 'GET':
    now = date.today()
    month = now.month
    year = now.year
    day = now.day

    customer_count = DailyEntry.objects.distinct().filter(date__day=day , date__month=month, date__year=year).count()

    coolers = DailyEntry.objects.distinct().filter(date__day=day, date__month=month, date__year=year).aggregate(Sum('cooler'))
    coolers_total = coolers['cooler__sum']

    today_coolers = DailyEntry.objects.filter(date__day=day, date__month=month, date__year=year)
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
      'data': 'DailyEntry not found.'}, status=status.HTTP_404_NOT_FOUND)

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
def daily_entry(request):
  if request.method == 'GET':
    dailyEntry = DailyEntry.objects.all()
    serializer = DailyEntrySerializerGET(dailyEntry, many=True)
    return JsonResponse(
      serializer.data, status=status.HTTP_200_OK, safe=False)

  if request.method == 'POST':
    data = request.data
    data_values = list(data.values())
    pk = data_values[0]
    print(data_values)
    # today_date = data_values[1]
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)
    # print(last_date.date())

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()
    # print(first_date)

    serializer = DailyEntrySerializer(data=request.data)

    if serializer.is_valid():
      serializer.save(addedby=request.user.username)
      serializer.save(customer=Customer.objects.get(pk=pk))
      print("Serializer Saved") 

      if datetime.date.today() == last_date.date():

        customer_name = Customer.objects.get(pk=pk).id

        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        total_cooler = DailyEntry.objects.filter(date__gte=start_day, date__lte=last_day).aggregate(Sum('cooler'))
        coolers_total = total_cooler['cooler__sum']

        if coolers_total is None:
          coolers = 0
        else:
          coolers = int(coolers_total)

        last_month_due_amount = CustomerAccount.objects.get(customer_name=pk)
        rate = Customer.objects.get(pk=pk).rate

        total = (int(coolers) * int(rate)) + int(last_month_due_amount.due)

        last_month_due_amount.due = int(total)
        last_month_due_amount.save()

        amount = int(coolers) * int(rate)

        bill_data = {
          'customer_name': pk,
          'to_date': last_day,
          'from_date': start_day,
          'coolers': coolers,
          'Pending_amount': last_month_due_amount,
          'Rate': rate,
          'Total': total,
          'Amount': amount
        }
        print(bill_data)
        data = bill_data
        data_values = list(data.values())
        pk = data_values[0]

        bill_serializer = GenerateBillSerializer(data=bill_data)
        if bill_serializer.is_valid():
          bill_serializer.save(addedby=request.user.username)
          customer = CustomerAccount.objects.get(customer_name=pk)
          customer.due = data_values[6]
          customer.updatedby = request.user.username
          customer.save()

        return JsonResponse(
          bill_serializer.data , status=status.HTTP_201_CREATED
        )

      return JsonResponse(
        serializer.data , status=status.HTTP_201_CREATED)


@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def payment(request):
  if request.method == 'POST':
    serializer = CustomerPaymentSerializer(data=request.data)

    # Conver the data to the list to get the each and every element from that data
    data = request.data
    data_values = list(data.values())
    pk = data_values[0]
    # Ends here

    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

    last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
    start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

    if serializer.is_valid():
      serializer.save(addedby=request.user.username)
      try:
        customer = CustomerAccount.objects.get(customer_name__id__in=Customer.objects.filter(route=data_values[1]))
        customer.due = int(customer.due) - int(data_values[2])
        customer.updatedby = request.user.username
      except:
        return JsonResponse({
          'error': "Customer is not this route"
        }, status=status.HTTP_400_BAD_REQUEST)

      try:
        customer_bill = CustomerBill.objects.filter(customer_name=pk).filter(paid=False).get(from_date=start_day)
        customer_bill.paid = True
        customer_bill.updatedby = request.user.username
        customer_bill.save()
        customer.save()
      except:
        return JsonResponse({
          'error': "Customer has not a Bill, First Generate Bill then try again!"
        }, status=status.HTTP_400_BAD_REQUEST)

      return JsonResponse({
        'detail': "Bill Paid and Customer Account Updated"
      }, status=status.HTTP_201_CREATED)

    return Response({
      'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

  if request.method == 'GET':
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)
    print(last_date.date())

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()
    print(first_date)

    customer_payment = CustomerPayment.objects.filter(date__gte=first_date, date__lte=last_date.date())
    customer_payment_serializer = CustomerPaymentSerializerGET(customer_payment, many=True)

    customer_payment_total = CustomerPayment.objects.filter(date__gte=first_date, date__lte=last_date.date()).aggregate(
      Sum('paid_amount'))
    total_paid_amount = customer_payment_total['paid_amount__sum']

    if total_paid_amount is None:
      total = 0
    else:
      total = total_paid_amount

    return JsonResponse({
      'data': customer_payment_serializer.data,
      'total paid amount': total
    }, status=status.HTTP_200_OK)


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


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def due_list_route(request, pk):
  if request.method == 'GET':

    try:
      route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
      return JsonResponse({
        'message': "Route Not Found"
      }, status=status.HTTP_404_NOT_FOUND)

    data_list = []
    customer_due_list = CustomerAccount.objects.filter(customer_name__id__in=Customer.objects.filter(route=pk))

    for i in customer_due_list:
      data_list.append({"customer_name": i.customer_name.name, "due": i.due})

    customer_due_list_filter = CustomerAccount.objects.filter(
      customer_name__id__in=Customer.objects.filter(route=pk)).aggregate(Sum('due'))
    customer_due_list_total = customer_due_list_filter['due__sum']

    if customer_due_list_total is None:
      total = 0
    else:
      total = customer_due_list_total

    return JsonResponse({
      'duelist_data': data_list,
      'due_total': total}, status=status.HTTP_200_OK)

  return Response({
    'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def due_list(request):
  if request.method == 'GET':

    customerdue = CustomerAccount.objects.all()

    data_list = []
    for i in customerdue:
      data_list.append({"customer_name": i.customer_name.name, "due": i.due})
      print(data_list)

    customer_due_list = CustomerAccount.objects.all().aggregate(Sum('due'))
    customer_due_list_total = customer_due_list['due__sum']

    if customer_due_list_total is None:
      total = 0
    else:
      total = customer_due_list_total

    return JsonResponse({
      'customer_due_list': data_list,
      'due_total': total
    }, status=status.HTTP_200_OK)


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


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def bill_detail(request, pk):
  if request.method == 'GET':
    try:
      bill = CustomerBill.objects.get(pk=pk)
    except CustomerBill.DoesNotExist:
      return JsonResponse({
        'message': "Bill Not Found"
      }, status=status.HTTP_400_BAD_REQUEST)

    customer_bill = GenerateBillSerializerGET(bill)
    customer_name = CustomerBill.objects.get(pk=pk).id

    daily_entry = DailyEntry.objects.filter(date_added__gte=bill.from_date, date_added__lte=bill.to_date).filter(
      customer=customer_name)
    daily_entry_serializer = DialyEntrySerializerGETDashboard(daily_entry, many=True)

    return JsonResponse({
      'bill': customer_bill.data,
      'daily_entry': daily_entry_serializer.data
    }, status=status.HTTP_200_OK)

  return JsonResponse({
    'message': "Something went wrong"
  }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def cutomer_payment_list(request, pk):
  if request.method == 'GET':
    try:
      customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
      return JsonResponse({
        'message': "Customer Not Found"
      }, status=status.HTTP_400_BAD_REQUEST)

    customer_payment = CustomerPayment.objects.filter(customer_name=customer.id)
    customer_payment_serializer = CustomerPaymentSerializerGET(customer_payment, many=True)

    customer_payment_total = CustomerPayment.objects.filter(customer_name=customer.id).aggregate(Sum('paid_amount'))
    total_paid_amount = customer_payment_total['paid_amount__sum']

    if total_paid_amount is None:
      total = 0
    else:
      total = total_paid_amount

    return JsonResponse({
      'data': customer_payment_serializer.data,
      'total paid amount': total
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def payment_list_route(request, pk):
  if request.method == 'GET':
    today_date = datetime.datetime.now()

    # Last day of month
    next_month = today_date.replace(day=28) + timedelta(days=4)
    last_date = next_month - timedelta(days=next_month.day)
    print(last_date.date())

    # First day of month
    first_date = datetime.datetime.today().replace(day=1).date()
    print(first_date)

    try:
      route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
      return JsonResponse({
        'message': "Route DoesNot Exists"
      })

    customer_payment_list = CustomerPayment.objects.filter(
      customer_name__id__in=Customer.objects.filter(route=pk)).filter(date__gte=first_date).filter(
      date__lte=last_date.date())
    customer_payment_serializer = CustomerPaymentSerializerGET(customer_payment_list, many=True)

    customer_payment_total = CustomerPayment.objects.filter(
      customer_name__id__in=Customer.objects.filter(route=pk)).filter(date__gte=first_date).filter(
      date__lte=last_date.date()).aggregate(Sum('paid_amount'))
    total_paid_amount = customer_payment_total['paid_amount__sum']

    if total_paid_amount is None:
      total = 0
    else:
      total = total_paid_amount

    return JsonResponse({
      'data': customer_payment_serializer.data,
      'total paid amount': total_paid_amount
    })
