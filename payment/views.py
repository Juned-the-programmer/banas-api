from datetime import date, timedelta
import datetime

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Sum

from bills.models import CustomerBill
from customer.models import CustomerAccount
from route.models import Route

from .models import *
from .serializer import *

# Create your views here.
@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def payment(request):
    if request.method == 'POST':
        serializer = CustomerPaymentSerializer(data=request.data)

        # Conver the data to the list to get the each and every element from that data
        data = request.data
        data_values = list(data.values())
        pk = data_values[0]
        if len(data_values) > 2:
            round_off = data_values[2]
        # Ends here

        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        if serializer.is_valid():
            try:
                customer = CustomerAccount.objects.get(customer_name=pk)
                customer.due = int(customer.due) - int(data_values[1])
                if len(data_values) > 2:
                    customer.due = int(customer.due) - int(data_values[2])
                customer.updatedby = request.user.username
            except:
                return JsonResponse({
                'error': "Customer Account Doesn't Exists ! "
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                customer_bill = CustomerBill.objects.filter(customer_name=pk).filter(paid=False).get(from_date=start_day)
                customer_bill.paid = True
                customer_bill.updatedby = request.user.username
                customer_bill.save()
            except:
                pass
                
            try:
                serializer.save(addedby=request.user.username , pending_amount=CustomerAccount.objects.get(customer_name=pk).due)
                customer.save()
                return JsonResponse({
                'detail': "Bill Paid and Customer Account Updated"
                }, status=status.HTTP_201_CREATED)
            except: 
                return JsonResponse({"message" : "Something went wrong while adding recors to database"}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return JsonResponse({"message" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

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
        
    return Response({
        'message': "Something went wrong, Please try again ! "}, status=status.HTTP_400_BAD_REQUEST)

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

        # First day of month
        first_date = datetime.datetime.today().replace(day=1).date()

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
            data_list.append({"customer_name": i.customer_name.first_name + ' ' + i.customer_name.last_name, "due": i.due})

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
        'message': "Something went wrong, Please Try again Later ! "}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
def due_list(request):
    if request.method == 'GET':

        customerdue = CustomerAccount.objects.all()

        data_list = []
        for i in customerdue:
            data_list.append({"customer_name": i.customer_name.first_name +' '+i.customer_name.last_name, "due": i.due})

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
    
    return JsonResponse({"message" : "Something went wrong, Please try again later ! "}, status=status.HTTP_400_BAD_REQUEST)