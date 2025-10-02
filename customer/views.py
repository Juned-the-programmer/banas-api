import datetime

from django.core.cache import cache
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from django.db.models import Sum

from rest_framework import generics, status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from customer.models import Customer, CustomerAccount
from customer.serializer import CustomerSerializer, CustomerSerializerList, CustomerAccountSerializer, CustomerDetailNestedSerializer
from dailyentry.models import DailyEntry, customer_daily_entry_monthly, customer_qr_code
from dailyentry.serializer import DailyEntrySerializerGETDashboard
from bills.models import CustomerBill
from bills.serializer import GenerateBillSerializerGET
from payment.models import CustomerPayment
from payment.serializer import CustomerPaymentSerializer, CustomerPaymentSerializerGET

from banas.cache_conf import customer_cached_data
from exception.views import *
from exception.error_constant import *

# Create your views here.
""" To POST customer and get the complete list of all the customer from database 
Validation for POST has been done by the serializer by itself don't want to customize here.
"""


class CustomerListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_serializer_class(self):
        method = self.request.method
        if method == "POST":
            return CustomerSerializer
        return CustomerSerializerList

    def perform_create(self, serializer):
        serializer.save(addedby=self.request.user.username)
        cache.delete("Customer")
        customer_cached_data()

    def get_queryset(self):
        return customer_cached_data().select_related("route")

''' Get all the customer with filter of Route. '''
class CustomerByRouteView(ListAPIView):
    serializer_class = CustomerSerializerList
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_queryset(self):
        route_id = self.kwargs["pk"]
        # Use cached data to avoid DB hits
        return customer_cached_data().filter(route=route_id, active=True)

''' Get the customer details and update customer details '''
class CustomerDetialUpdateView(RetrieveUpdateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        # Always use cache instead of DB
        return customer_cached_data()

    def perform_update(self, serializer):
        serializer.save(updatedby=self.request.user.username)
        cache.delete("Customer")
        customer_cached_data()

class CustomerAccountUpdateView(UpdateAPIView):
    serializer_class = CustomerAccountSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        # Optimized: fetch customer and related account in one query
        return Customer.objects.select_related("customer_account")

    def get_object(self):
        # Still need to return the account for the serializer
        try:
            customer = self.get_queryset().get(id=self.kwargs["pk"])
            return customer.customer_account
        except Customer.DoesNotExist:
            raise NotFound(detail=f"Customer {self.kwargs['pk']} not found")

    def perform_update(self, serializer):
        serializer.save(updatedby=self.request.user.username)
        # Refresh cache
        cache.delete("Customer")
        customer_cached_data()

class CustomerDetailView(RetrieveAPIView):
    serializer_class = CustomerDetailNestedSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        """
        Optimize queries using select_related (OneToOne) and prefetch_related (reverse FK)
        """
        return Customer.objects.select_related(
            'customer_account',
            'customer_daily_entry_monthly',
            'customer_qr_code'
        ).prefetch_related(
            'customer_bill',
            'customer_daily_entry',
            'customer_payment__customer_name'
        )

    def get_object(self):
        try:
            customer = self.get_queryset().get(id=self.kwargs['pk'])
            return customer
        except Customer.DoesNotExist:
            raise NotFound(detail=f"Customer {self.kwargs['pk']} not found")
