import datetime
from datetime import date, timedelta
from django.utils import timezone

from django.core.cache import cache
from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from banas.cache_conf import customer_cached_data
from bills.models import CustomerBill
from customer.models import Customer, CustomerAccount
from exception.views import customer_not_found_exception, route_not_found_exception, serializer_errors
from route.models import Route
from banas.cache_conf import total_pending_due_cached

from .models import CustomerPayment
from .serializer import CustomerPaymentSerializer, CustomerPaymentSerializerGET


# -------------------------------
# Create & List Payments
# -------------------------------
class PaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = CustomerPaymentSerializer

    def get_queryset(self):
        today = timezone.localdate()
        first_day = today.replace(day=1)
        
        # We query the range to use the index efficiently
        return CustomerPayment.objects.select_related("customer_name").filter(
            date__date__gte=first_day,
            date__date__lte=today
        ).order_by("-date")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CustomerPaymentSerializerGET(queryset, many=True)

        total_paid_amount = queryset.aggregate(Sum("paid_amount"))["paid_amount__sum"] or 0

        return Response(
            {"payments": serializer.data, "total paid amount": total_paid_amount},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = CustomerPaymentSerializer(data=request.data)
        data_values = list(request.data.values())

        if not serializer.is_valid():
            return serializer_errors(serializer.errors)

        pk = data_values[0]
        round_off = data_values[2] if len(data_values) > 2 else 0

        # Previous month date range
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        try:
            customer = CustomerAccount.objects.get(customer_name=pk)
        except CustomerAccount.DoesNotExist:
            return customer_not_found_exception(pk)

        with transaction.atomic():
            # Capture pending amount BEFORE updating
            pending_amount_before_payment = int(customer.due)

            # Update customer account
            customer.due = int(customer.due) - int(data_values[1]) - int(round_off)
            customer.total_paid = int(customer.total_paid) + int(data_values[1])
            customer.updatedby = request.user.username

            # Mark unpaid bill of prev month as paid if exists
            CustomerBill.objects.filter(customer_name=pk, paid=False, from_date=start_day).update(
                paid=True, updatedby=request.user.username
            )

            # Save payment record with pending amount BEFORE payment was made
            serializer.save(addedby=request.user.username, pending_amount=pending_amount_before_payment)
            customer.save()

        # Invalidate the due cache — next dashboard call will recompute from DB
        cache.delete("total_pending_due")
        total_pending_due_cached()

        return Response(
            {"detail": "Bill Paid and Customer Account Updated"},
            status=status.HTTP_201_CREATED,
        )


# -------------------------------
# List Payments by Customer
# -------------------------------
class CustomerPaymentListView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = CustomerPaymentSerializerGET

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return CustomerPayment.objects.select_related("customer_name").filter(customer_name=pk)

    def list(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        try:
            customer_data = customer_cached_data()
            customer = customer_data.get(id=pk)
        except Exception:
            return customer_not_found_exception(pk)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        total_paid_amount = customer.customer_account.total_paid or 0

        return Response(
            {"payments": serializer.data, "total paid amount": total_paid_amount},
            status=status.HTTP_200_OK,
        )


# -------------------------------
# Payments by Route
# -------------------------------
class PaymentListByRouteView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = CustomerPaymentSerializerGET

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        today = timezone.localdate()
        first_day = today.replace(day=1)

        return CustomerPayment.objects.select_related("customer_name").filter(
            customer_name__route_id=pk,
            date__gte=first_day,
            date__lte=today
        ).order_by("-date")

    def list(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        try:
            Route.objects.get(pk=pk)
        except Route.DoesNotExist:
            return route_not_found_exception(pk)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        total_paid_amount = queryset.aggregate(Sum("paid_amount"))["paid_amount__sum"] or 0

        return Response(
            {"payments": serializer.data, "total paid amount": total_paid_amount},
            status=status.HTTP_200_OK,
        )


# -------------------------------
# Due by Route
# -------------------------------
class DueListByRouteView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def list(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        if not Route.objects.filter(pk=pk).exists():
            return route_not_found_exception(pk)

        customer_accounts = CustomerAccount.objects.select_related("customer_name").filter(
            customer_name__route_id=pk,
            customer_name__active=True
        ).order_by('customer_name__first_name')

        data_list = [
            {
                "customer_id": acc.customer_name.id,
                "customer_name": f"{acc.customer_name.first_name} {acc.customer_name.last_name}",
                "due": acc.due,
            }
            for acc in customer_accounts
        ]

        # Aggregate total due by route
        due_total = customer_accounts.aggregate(Sum("due"))["due__sum"] or 0

        return Response(
            {"customer_due_list": data_list, "due_total": due_total},
            status=status.HTTP_200_OK,
        )


# -------------------------------
# Total Due (All Customers)
# -------------------------------
class DueListView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def list(self, request, *args, **kwargs):
        customer_due_qs = CustomerAccount.objects.filter(
            customer_name__active=True
        ).values(
            "customer_name__id", 
            "customer_name__first_name", 
            "customer_name__last_name", 
            "due"
        ).order_by("customer_name__first_name")

        data_list = [
            {
                "customer_id": item["customer_name__id"],
                "customer_name": f"{item['customer_name__first_name']} {item['customer_name__last_name']}",
                "due": item["due"],
            }
            for item in customer_due_qs
        ]

        due_total = CustomerAccount.calculate_total_due()

        return Response(
            {"customer_due_list": data_list, "due_total": due_total},
            status=status.HTTP_200_OK,
        )
