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
        # Ends here

        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        if serializer.is_valid():
            try:
                customer = CustomerAccount.objects.get(customer_name=pk)
                customer.due = int(customer.due) - int(data_values[1])
                customer.updatedby = request.user.username
            except:
                return JsonResponse({
                'error': "Customer Account Doesn't Exists ! "
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                customer_bill = CustomerBill.objects.filter(customer_name=pk).filter(paid=False).get(from_date=start_day)
                customer_bill.paid = True
                customer_bill.updatedby = request.user.username
            except:
                return JsonResponse({
                'error': "Customer has not a Bill, First Generate Bill then try again!"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                serializer.save(addedby=request.user.username , pending_amount=CustomerAccount.objects.get(customer_name=pk).due)
                customer.save()
                customer_bill.save()
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
