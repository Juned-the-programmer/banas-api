import datetime
from datetime import time

from django.db import connection
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
# List missing daily entries for today
# -------------------------------
class MissingDailyEntryView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self, request):
        route_id = request.query_params.get("route")

        today = timezone.localdate()
        start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))

        qs = Customer.objects.filter(active=True)
        if route_id:
            qs = qs.filter(route_id=route_id)

        missing = (
            qs.annotate(
                today_entries=Count(
                    "customer_daily_entry",
                    filter=Q(customer_daily_entry__date_added__gte=start, customer_daily_entry__date_added__lte=end),
                )
            )
            .filter(today_entries=0)
            .values("id", "first_name", "last_name")
        )

        missing_list = list(missing)

        return Response(
            {
                "date": today,
                "route": route_id,
                "missing_count": len(missing_list),
                "customers": missing_list,
            }
        )


# -------------------------------
# Customer QR daily entry (function-based)
# -------------------------------
def customer_qr_daily_entry(request, pk):
    try:
        customer_obj = Customer.objects.get(id=pk)
    except Customer.DoesNotExist:
        return render(request, "dailyentry/dailyentrytime.html", {"error": "Customer not found."})

    context = {
        "customer": customer_obj,
        "error_message": None,
        "success_message": None,
    }

    if request.method == "POST":
        try:
            qr_data = customer_qr_code.objects.get(customer=pk)
            qr_code_pin = qr_data.qrcode_pin
        except customer_qr_code.DoesNotExist:
            qr_code_pin = None

        submitted_pin = request.POST.get("pin", "")
        
        try:
            submitted_pin_int = int(submitted_pin)
        except ValueError:
            submitted_pin_int = None

        if qr_code_pin is not None and qr_code_pin == submitted_pin_int:
            coolers_val = request.POST.get("coolers", "0")
            try:
                pending_daily_entry_customer = pending_daily_entry(
                    customer=customer_obj, 
                    coolers=int(coolers_val)
                )
                pending_daily_entry_customer.save()
                context["success_message"] = f"Successfully recorded {coolers_val} coolers!"
            except ValueError:
                context["error_message"] = "Invalid cooler quantity."
        else:
            context["error_message"] = "Incorrect PIN."

    current_time = datetime.datetime.now().time()
    
    # Check if within valid hours (9 AM to 6 PM)
    if time(9, 0, 0) <= current_time <= time(18, 0, 0):
        return render(request, "dailyentry/dailyentry.html", context)
    else:
        # Pass context so we can say "Dear Juned, portal closed"
        return render(request, "dailyentry/dailyentrytime.html", context)


# -------------------------------
# Customer Update PIN (function-based)
# -------------------------------
def customer_update_pin(request, pk):
    try:
        customer_obj = Customer.objects.get(id=pk)
    except Customer.DoesNotExist:
        return render(request, "dailyentry/dailyentrytime.html", {"error": "Customer not found."})

    context = {
        "customer": customer_obj,
        "error_message": None,
        "success_message": None,
    }

    if request.method == "POST":
        current_pin_input = request.POST.get("current_pin", "")
        new_pin_input = request.POST.get("new_pin", "")

        try:
            qr_data = customer_qr_code.objects.get(customer=pk)
            # Verify current PIN matches
            if int(current_pin_input) == qr_data.qrcode_pin:
                # Update to new PIN
                qr_data.qrcode_pin = int(new_pin_input)
                qr_data.save()
                context["success_message"] = "Your PIN has been successfully updated! You can now use it for daily entries."
            else:
                context["error_message"] = "The current PIN you entered is incorrect."
        except customer_qr_code.DoesNotExist:
             context["error_message"] = "No PIN is configured for this account yet."
        except ValueError:
             context["error_message"] = "PIN must be a valid number."

    return render(request, "dailyentry/update_pin.html", context)


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

