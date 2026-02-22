import datetime
from datetime import time

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from banas.cache_conf import customer_cached_data
from customer.models import Customer
from dailyentry.task import verify_and_commit_pending_entries, bulk_import_daily_entries

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
        today = timezone.localdate()
        start_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
        return DailyEntry.objects.filter(date_added__gte=start_of_day,date_added__lte=end_of_day).select_related("customer")

    def perform_create(self, serializer):
        # Set date_added if not provided
        if not serializer.validated_data.get('date_added'):
            serializer.save(addedby=self.request.user.username, date_added=timezone.now())
        else:
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

        # Enqueue to QStash — task handles all DB writes
        entries = [{"customer": str(item["customer"].id), "cooler": item["cooler"]} for item in serializer.validated_data]
        bulk_import_daily_entries(entries)

        return Response({"message": "Bulk import queued!"}, status=status.HTTP_202_ACCEPTED)


# -------------------------------
# Verify pending daily entries
# -------------------------------
class VerifyPendingDailyEntryView(generics.CreateAPIView):
    serializer_class = DailyEntryVerifyResultSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # Enqueue to QStash — task handles all DB writes
        entries = [
            {
                "id": str(item.get("id", "")),
                "customer": str(item.get("customer", "")),
                "coolers": item.get("coolers"),
                "date_added": item.get("date_added").isoformat() if item.get("date_added") else None,
            }
            for item in serializer.validated_data
        ]
        verify_and_commit_pending_entries(entries)

        return Response({"message": "Verification queued!"}, status=status.HTTP_202_ACCEPTED)


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
# Scheduled Task Endpoints (Called by QStash)
# -------------------------------
from django.views.decorators.csrf import csrf_exempt
from .task import reset_dailentry_dashboard_values


@csrf_exempt
def run_reset_dashboard_task(request):
    """
    HTTP endpoint for QStash to trigger dashboard reset.
    Called via cron schedule: Daily at 00:01
    """
    if request.method == "POST":
        try:
            reset_dailentry_dashboard_values()
            return JsonResponse({"status": "success", "message": "Dashboard reset completed"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

