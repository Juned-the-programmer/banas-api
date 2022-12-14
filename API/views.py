from rest_framework.decorators import api_view, permission_classes
import datetime
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
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
      daily_entry = DailyEntry.objects.filter(date=today_date - timedelta(days=i)).aggregate(Sum('cooler'))
      coolers_total = daily_entry['cooler__sum']

      if coolers_total is None:
        coolers = 0
      else:
        coolers = coolers_total

      data_list.append({"date": str(today_date - timedelta(days=i)), "coolers": coolers})

    return JsonResponse({
      'status': '200',
      'data': data_list
    }, status=status.HTTP_200_OK)

  if request.method == 'POST':
    date_data = request.data
    data_values = list(date_data.values())

    # Configuring date
    from_date = datetime.datetime.strptime(data_values[0], "%Y-%m-%d")
    to_date = datetime.datetime.strptime(data_values[1], "%Y-%m-%d")
    days = to_date - from_date

    data_list = []

    for i in range(0, int(days.days)):
      daily_entry = DailyEntry.objects.filter(date=to_date - timedelta(days=i)).aggregate(Sum('cooler'))
      coolers_total = daily_entry['cooler__sum']

      if coolers_total is None:
        coolers = 0
      else:
        coolers = coolers_total

      data_list.append({"date": str(to_date - timedelta(days=i)), "coolers": coolers})

    return JsonResponse({
      'status': '200',
      'data': data_list
    }, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': '400',
    'data': "There is some error, Please try again!"
  }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def get_profile(request):
  user = User.objects.get(username=request.user.username)

  return JsonResponse({
    'status': 200,
    'username': user.username,
    'id': user.id,
    'first_name': user.first_name,
    'last_name': user.last_name,
    'full_name': user.first_name + ' ' + user.last_name,
    'is_superuser': user.is_superuser,
    'email': user.email}, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def route(request):
  if request.method == 'POST':
    route_data = request.data
    route_serializer = RouteSerializer(data=route_data)

    if route_serializer.is_valid():
      route_serializer.save(addedby=request.user.username)

      return JsonResponse({
        'status': 200,
        'data': route_serializer.data}, status=status.HTTP_200_OK)

    return JsonResponse({
      'status': 400,
      'data': route_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

  if request.method == 'GET':
    routes = Route.objects.all()
    serializer = RouteSerializer(routes, many=True)
    return JsonResponse({
      'status': 200,
      'data': serializer.data}, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET', 'DELETE'])
@permission_classes([IsAdminUser, IsAuthenticated])
def view_update_delete_route(request, pk):
  try:
    route = Route.objects.get(pk=pk)
  except Route.DoesNotExist:
    return JsonResponse({
      'status': 404,
      'data': 'Route not found.'}, status=status.HTTP_404_NOT_FOUND)

  if request.method == 'PUT':
    serializer = RouteSerializer(route, data=request.data)
    if serializer.is_valid():
      serializer.save(updatedby=request.user.username)
      return JsonResponse({
        'status': 201,
        'data': serializer.data}, status=status.HTTP_201_CREATED)

    return JsonResponse({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
  if request.method == 'GET':
    route = Route.objects.get(pk=pk)
    serializer = RouteSerializerGET(route)
    return JsonResponse({
      'status': 200,
      'data': serializer.data}, status=status.HTTP_200_OK)
  if request.method == 'DELETE':
    route = Route.objects.get(pk=pk)
    serializer = RouteSerializerGET(route)
    route.delete()
    return JsonResponse({
      'status': 200,
      'message': 'Route deleted successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
  return JsonResponse({
    'status': 400,
    'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def customer(request):
  if request.method == 'POST':
    data = request.data
    data_values = list(data.values())
    pk = data_values[0]

    customer_data = {
      "name": data_values[0],
      "route": data_values[1],
      "rate": data_values[2]
    }

    customer_serializer = CustomerSerializer(data=customer_data)

    if customer_serializer.is_valid():
      customer_serializer.save(addedby=request.user.username)
      if (len(data_values) > 3):
        customeraccount = CustomerAccount.objects.get(customer_name=Customer.objects.get(name=data_values[0]).id)
        customeraccount.due = data_values[3]
        customeraccount.updatedby = request.user.username
        customeraccount.save()

      return JsonResponse({
        'status': 201,
        'data': customer_serializer.data}, status=status.HTTP_201_CREATED)

    return JsonResponse({
      'status': 400,
      'data': customer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

  if request.method == 'GET':
    customers = Customer.objects.all()
    serializer = CustomerSerializerGET(customers, many=True)
    return JsonResponse({
      'status': 200,
      'data': serializer.data}, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


def list_customer_by_route(request, pk):
  if request.method == 'GET':
    customer_route = Customer.objects.filter(route=pk)
    customer_route_serializer = CustomerSerializerGET(customer_route, many=True)

    return JsonResponse({
      'status': 200,
      'data': customer_route_serializer.data
    })


@api_view(['PUT', 'GET', 'DELETE'])
@permission_classes([IsAdminUser, IsAuthenticated])
def view_update_delete_customer(request, pk):
  try:
    customer = Customer.objects.get(pk=pk)
  except Customer.DoesNotExist:
    return JsonResponse({
      'status': 404,
      'data': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

  if request.method == 'PUT':
    serializer = CustomerSerializer(customer, data=request.data)
    if serializer.is_valid():
      serializer.save(updatedby=request.user.username)
      return JsonResponse({
        'status': 201,
        'data': serializer.data}, status=status.HTTP_201_CREATED)

    return JsonResponse({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
  if request.method == 'GET':
    customer = Customer.objects.get(pk=pk)
    serializer = CustomerSerializerGET(customer)
    return JsonResponse({
      'status': 200,
      'data': serializer.data}, status=status.HTTP_200_OK)
  if request.method == 'DELETE':
    customer = Customer.objects.get(pk=pk)
    serializer = CustomerSerializerGET(customer)
    customer.delete()
    return JsonResponse({
      'status': 200,
      'message': 'Customer deleted successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry_count(request):
  if request.method == 'GET':
    customer_count = DailyEntry.objects.distinct().filter(date=date.today()).count()

    coolers = DailyEntry.objects.distinct().filter(date=date.today()).aggregate(Sum('cooler'))
    coolers_total = coolers['cooler__sum']

    today_coolers = DailyEntry.objects.filter(date=date.today())
    today_coolers_serializer = DailyEntrySerializerGET(today_coolers, many=True)

    if coolers_total is None:
      total = 0
    else:
      total = coolers_total

    return JsonResponse(
      {'status': 200,
       'data': today_coolers_serializer.data,
       'customer_count': customer_count,
       'coolers_total': total}, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def view_delete_daily_entry(request, pk):
  try:
    dailyEntry = DailyEntry.objects.get(pk=pk)
  except DailyEntry.DoesNotExist:
    return JsonResponse({
      'status': 404,
      'data': 'DailyEntry not found.'}, status=status.HTTP_404_NOT_FOUND)
  if request.method == 'DELETE':
    dailyEntry = DailyEntry.objects.get(pk=pk)
    dailyEntry.delete()
    return JsonResponse({
      'status': 200,
      'message': 'DailyEntry deleted successfully'}, status=status.HTTP_200_OK)

    return JsonResponse({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
  if request.method == 'PUT':
    serializer = DailyEntrySerializer(dailyEntry, data=request.data)
    if serializer.is_valid():
      serializer.save(updatedby=request.user.username)
      return JsonResponse({
        'status': 201,
        'data': serializer.data}, status=status.HTTP_201_CREATED)

    return JsonResponse({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
  if request.method == 'GET':
    dailyEntry = DailyEntry.objects.get(pk=pk)
    serializer = DailyEntrySerializerGETSingle(dailyEntry)
    return JsonResponse({
      'status': 200,
      'data': serializer.data}, status=status.HTTP_200_OK)

    return JsonResponse({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAdminUser, IsAuthenticated])
def daily_entry(request):
  if request.method == 'GET':
    dailyEntry = DailyEntry.objects.all()
    serializer = DailyEntrySerializerGET(dailyEntry, many=True)
    return JsonResponse({
      'status': 200,
      'data': serializer.data}, status=status.HTTP_200_OK)
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

        last_month_due_amount = CustomerAccount.objects.get(customer_name=pk).due
        rate = Customer.objects.get(pk=pk).rate

        total = (int(coolers) * int(rate)) + int(last_month_due_amount)

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

      return JsonResponse({
        'status': 201,
        'data': serializer.data}, status=status.HTTP_201_CREATED)


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
          'status': 400,
          'detail': "Customer is not this route"
        }, status=status.HTTP_400_BAD_REQUEST)

      try:
        customer_bill = CustomerBill.objects.filter(customer_name=pk).filter(paid=False).get(from_date=start_day)
        customer_bill.paid = True
        customer_bill.updatedby = request.user.username
        customer_bill.save()
        customer.save()
      except:
        return JsonResponse({
          'status': 400,
          'detail': "Customer has not a Bill, First Generate Bill then try again!"
        }, status=status.HTTP_400_BAD_REQUEST)

      return JsonResponse({
        'status': 200,
        'detail': "Bill Paid and Customer Account Updated"
      }, status=status.HTTP_201_CREATED)

    return Response({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
      'status': 200,
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
      'status': 400,
      'data': "Customer Not Found"
    }, status=status.HTTP_404_NOT_FOUND)

  if request.method == 'PUT':
    serializer = CustomerAccountSerializer(customer, data=request.data)
    if serializer.is_valid():
      serializer.save(updatedby=request.user.username)
      return JsonResponse({
        'status': 200,
        'data': serializer.data
      }, status=status.HTTP_201_CREATED)

    return JsonResponse({
      'status': 400,
      'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def due_list_route(request, pk):
  if request.method == 'GET':

    try:
      route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
      return JsonResponse({
        'status': 400,
        'data': "Route Not Found"
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
      'status': 200,
      'duelist_data': data_list,
      'due_total': total}, status=status.HTTP_200_OK)

  return Response({
    'status': 400,
    'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
      'status': 200,
      'duelist_data': data_list,
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
        'status': 400,
        'data': "Customer Not Found"
      }, status=status.HTTP_400_BAD_REQUEST)

    customer_due = customer.due
    return JsonResponse({
      'status': 200,
      'customer_name': customer.customer_name.name,
      'due': customer_due}, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': "Something went wrong"
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
        'status': 400,
        'data': "Customer Not Found"
      }, status=status.HTTP_400_BAD_REQUEST)

    customer_detail = customer
    detail_serializer = CustomerSerializerGET(customer_detail)

    customer_bills = CustomerBill.objects.filter(customer_name=customer.id)
    bill_serializer = DetailBillSerializer(customer_bills, many=True)

    customer_daily_entry = DailyEntry.objects.filter(date__gte=first_day_of_month).filter(customer_name=customer.id)
    daily_entry_serializer = DialyEntrySerializerGETDashboard(customer_daily_entry, many=True)

    customer_daily_entry_total = DailyEntry.objects.filter(date__gte=first_day_of_month).filter(
      customer_name=customer.id).aggregate(Sum("cooler"))
    total_coolers = customer_daily_entry_total['cooler__sum']

    if total_coolers is None:
      total = 0
    else:
      total = total_coolers

    return JsonResponse({
      'status': 200,
      'customer_detail': detail_serializer.data,
      'bills': bill_serializer.data,
      'daily_entry': daily_entry_serializer.data,
      'total_coolers': total
    }, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': "Something Went Wrong"
  }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def bill_detail(request, pk):
  if request.method == 'GET':
    try:
      bill = CustomerBill.objects.get(pk=pk)
    except CustomerBill.DoesNotExist:
      return JsonResponse({
        'status': 400,
        'data': "Bill Not Found"
      }, status=status.HTTP_400_BAD_REQUEST)

    customer_bill = GenerateBillSerializerGET(bill)
    customer_name = CustomerBill.objects.get(pk=pk).id

    daily_entry = DailyEntry.objects.filter(date__gte=bill.from_date, date__lte=bill.to_date).filter(
      customer_name=customer_name)
    daily_entry_serializer = DialyEntrySerializerGETDashboard(daily_entry, many=True)

    return JsonResponse({
      'status': 200,
      'bill': customer_bill.data,
      'daily_entry': daily_entry_serializer.data
    }, status=status.HTTP_200_OK)

  return JsonResponse({
    'status': 400,
    'data': "Something went wrong"
  }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def cutomer_payment_list(request, pk):
  if request.method == 'GET':
    try:
      customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
      return JsonResponse({
        'status': 400,
        'data': "Customer Not Found"
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
      'status': 200,
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
        'status': 400,
        'data': "Route DoesNot Exists"
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
      'status': 200,
      'data': customer_payment_serializer.data,
      'total paid amount': total_paid_amount
    })
