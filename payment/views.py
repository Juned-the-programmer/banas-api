import datetime
from datetime import date, timedelta

from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from bills.models import CustomerBill
from customer.models import Customer, CustomerAccount
from route.models import Route
from banas.cache_conf import customer_cached_data
from exception.views import (
    customer_not_found_exception,
    route_not_found_exception,
    serializer_errors,
    internal_server_error,
)

from .models import CustomerPayment
from .serializer import CustomerPaymentSerializer, CustomerPaymentSerializerGET


# -------------------------------
# Create & List Payments
# -------------------------------
class PaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = CustomerPaymentSerializer

    def get_queryset(self):
        return CustomerPayment.objects.select_related("customer_name").all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CustomerPaymentSerializerGET(queryset, many=True)

        total_paid_amount = queryset.aggregate(Sum("paid_amount"))["paid_amount__sum"] or 0

        return Response(
            {"data": serializer.data, "total paid amount": total_paid_amount},
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
        last_day = last_day_of_prev_month.strftime("%Y-%m-%d")
        start_day = start_day_of_prev_month.strftime("%Y-%m-%d")

        try:
            customer = CustomerAccount.objects.get(customer_name=pk)
        except CustomerAccount.DoesNotExist:
            return customer_not_found_exception(pk)

        # Update customer account
        customer.due = int(customer.due) - int(data_values[1]) - int(round_off)
        customer.total_paid = int(customer.total_paid) + int(data_values[1])
        customer.updatedby = request.user.username

        # Mark unpaid bill of prev month as paid if exists
        CustomerBill.objects.filter(
            customer_name=pk, paid=False, from_date=start_day
        ).update(paid=True, updatedby=request.user.username)

        # Save payment record
        serializer.save(addedby=request.user.username, pending_amount=customer.due)
        customer.save()

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
            {"data": serializer.data, "total paid amount": total_paid_amount},
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
        today_date = datetime.datetime.now()
        next_month = today_date.replace(day=28) + timedelta(days=4)
        last_date = next_month - timedelta(days=next_month.day)
        first_date = today_date.replace(day=1).date()

        return CustomerPayment.objects.select_related("customer_name").filter(
            customer_name__id__in=Customer.objects.filter(route=pk),
            date__gte=first_date,
            date__lte=last_date.date(),
        )

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
            {"data": serializer.data, "total paid amount": total_paid_amount},
            status=status.HTTP_200_OK,
        )


# -------------------------------
# Due by Route
# -------------------------------
class DueListByRouteView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def list(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        try:
            Route.objects.get(pk=pk)
        except Route.DoesNotExist:
            return route_not_found_exception(pk)

        customer_due_list = CustomerAccount.objects.select_related("customer_name").filter(
            customer_name__id__in=Customer.objects.filter(route=pk)
        )

        data_list = [
            {
                "customer_id": acc.customer_name.id,
                "customer_name": f"{acc.customer_name.first_name} {acc.customer_name.last_name}",
                "due": acc.due,
            }
            for acc in customer_due_list
        ]

        # Aggregate total due by route
        total_due_by_route = CustomerAccount.calculate_total_due_route()
        customer_due_list_total = next(
            (route["total_due"] for route in total_due_by_route if str(route["customer_name__route"]) == str(pk)), 0
        )

        return Response(
            {"duelist_data": data_list, "due_total": customer_due_list_total},
            status=status.HTTP_200_OK,
        )


# -------------------------------
# Total Due (All Customers)
# -------------------------------
class DueListView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def list(self, request, *args, **kwargs):
        customerdue = CustomerAccount.objects.select_related("customer_name").all()

        data_list = [
            {
                "customer_id": acc.customer_name.id,
                "customer_name": f"{acc.customer_name.first_name} {acc.customer_name.last_name}",
                "due": acc.due,
            }
            for acc in customerdue
        ]

        customer_due_list_total = CustomerAccount.calculate_total_due() or 0

        return Response(
            {"customer_due_list": data_list, "due_total": customer_due_list_total},
            status=status.HTTP_200_OK,
        )