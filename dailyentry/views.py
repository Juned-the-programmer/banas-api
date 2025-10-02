import datetime
from datetime import date, time, timedelta

from django.db import connection
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from banas.cache_conf import customer_cached_data
from customer.models import Customer
from exception.views import internal_server_error

from .models import DailyEntry, DailyEntry_dashboard, customer_qr_code, pending_daily_entry
from .serializer import (
    DailyEntryBulkImportSerializer,
    DailyEntrySerializer,
    DailyEntrySerializerGETDashboard,
    DailyEntrySerializerGETSingle,
    DailyEntryVerifyResultSerializer,
    PendingDailyEntrySerializer,
)


# -------------------------------
# List today's entries & create new entry
# -------------------------------
class DailyEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyEntrySerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_queryset(self):
        today = datetime.datetime.now().date()
        return DailyEntry.objects.filter(date_added__date=today).select_related("customer")

    def perform_create(self, serializer):
        serializer.save(addedby=self.request.user.username)


# -------------------------------
# Count summary for dashboard
# -------------------------------
class DailyEntryCountView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        dashboard = DailyEntry_dashboard.objects.first()
        return Response(
            {
                "today_customer_count": dashboard.customer_count if dashboard else 0,
                "today_coolers_total": dashboard.coolers_count if dashboard else 0,
            }
        )


# -------------------------------
# Retrieve, Update, Delete a single entry
# -------------------------------
class DailyEntryDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyEntrySerializerGETSingle
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = DailyEntry.objects.select_related("customer")
    lookup_field = "pk"

    def perform_update(self, serializer):
        serializer.save(updatedby=self.request.user.username)


# -------------------------------
# Bulk import entries
# -------------------------------
class DailyEntryBulkImportView(generics.CreateAPIView):
    serializer_class = DailyEntryBulkImportSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        addedby = request.user.username
        daily_entries = [
            DailyEntry(customer=item["customer"], cooler=item["cooler"], addedby=addedby, date_added=timezone.now())
            for item in serializer.validated_data
        ]
        DailyEntry.objects.bulk_create(daily_entries)

        return Response({"message": "Bulk Import success!"}, status=status.HTTP_201_CREATED)


# -------------------------------
# Verify pending daily entries
# -------------------------------
class VerifyPendingDailyEntryView(generics.CreateAPIView):
    serializer_class = DailyEntryVerifyResultSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        addedby = request.user.username
        daily_entries = []
        pending_ids = []

        customer_data = customer_cached_data()

        for item in serializer.validated_data:
            customer_id = item.get("customer")
            cooler = item.get("cooler")
            date_added = item.get("date_added")
            pending_id = item.get("pending_id")
            pending_ids.append(pending_id)

            try:
                customer = customer_data.get(id=customer_id)
                daily_entries.append(
                    DailyEntry(
                        customer=customer,
                        cooler=cooler,
                        addedby=f"{customer.first_name} {customer.last_name}",
                        date_added=date_added,
                    )
                )
            except Customer.DoesNotExist:
                return Response({"error": f"Customer {customer_id} not found"}, status=status.HTTP_400_BAD_REQUEST)

        if daily_entries:
            DailyEntry.objects.bulk_create(daily_entries)
            pending_daily_entry.objects.filter(id__in=pending_ids).delete()

        return Response({"message": "Verified Successfully!"}, status=status.HTTP_200_OK)


# -------------------------------
# List pending daily entries
# -------------------------------
class PendingDailyEntryListView(generics.ListAPIView):
    serializer_class = PendingDailyEntrySerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = pending_daily_entry.objects.select_related("customer")


# -------------------------------
# Customer QR daily entry (function-based)
# -------------------------------
def customer_qr_daily_entry(request, pk):
    if request.method == "POST":
        qr_code_pin = customer_qr_code.objects.get(customer=pk).qrcode_pin

        if qr_code_pin == int(request.POST.get("pin", 0)):
            pending_daily_entry_customer = pending_daily_entry(
                customer=Customer.objects.get(id=pk), coolers=int(request.POST.get("coolers", 0))
            )
            pending_daily_entry_customer.save()

    current_time = datetime.datetime.now().time()
    if time(9, 0, 0) < current_time < time(18, 0, 0):
        return render(request, "dailyentry/dailyentry.html")
    else:
        return render(request, "dailyentry/dailyentrytime.html")


# -------------------------------
# Historical data retriever
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAdminUser, IsAuthenticated])
def historical_data_retriever(request):
    params = request.GET.get("historical")
    table_name = f"dailyentry_{params}"

    # Check table existence
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT to_regclass('{table_name}')")
        if not cursor.fetchone()[0]:
            return JsonResponse({"error": "Table not found"}, status=404)

    # Fetch data
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    old_data = [dict(zip(columns, row)) for row in rows]
    serialized_data = DailyEntrySerializerGETDashboard(old_data, many=True)
    return JsonResponse({f"historical_{params}": serialized_data.data}, status=status.HTTP_200_OK, safe=False)
