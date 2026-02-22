import datetime
from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from customer.models import Customer, CustomerAccount
from dailyentry.models import customer_daily_entry_monthly, DailyEntry
from dailyentry.serializer import DailyEntrySerializerGETDashboard
from exception.views import customer_not_found_exception

from .models import CustomerBill
from .serializer import GenerateBillSerializer, GenerateBillSerializerGET
from .utils import bill_number_generator

# create your view here


# List all bills
class BillListView(generics.ListAPIView):
    serializer_class = GenerateBillSerializerGET
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_queryset(self):
        return CustomerBill.objects.select_related("customer_name").all()


# Retrieve a bill + its daily entries
class BillDetailView(generics.RetrieveAPIView):
    serializer_class = GenerateBillSerializerGET
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = CustomerBill.objects.select_related("customer_name")
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        bill = self.get_object()

        start_datetime = timezone.make_aware(
            datetime.datetime.combine(bill.from_date, datetime.time.min)
        )

        end_datetime = timezone.make_aware(
            datetime.datetime.combine(bill.to_date, datetime.time.max)
        )

        daily_entries = DailyEntry.objects.filter(
            customer=bill.customer_name,
            date_added__gte=start_datetime,
            date_added__lte=end_datetime
        ).order_by('date_added')

        daily_entry_serializer = DailyEntrySerializerGETDashboard(daily_entries, many=True)
        bill_serializer = self.get_serializer(bill)

        return Response({
            "bill": bill_serializer.data, 
            "daily_entry": daily_entry_serializer.data
        })


# Generate a new bill for a customer
class GenerateBillView(generics.CreateAPIView):
    serializer_class = GenerateBillSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return customer_not_found_exception(pk)

        today_date = datetime.datetime.now()

        # Better to use Django's timezone to avoid server time mismatches
        today_date = timezone.now().date()

        # Calculate date range directly as date objects
        first_date = today_date.replace(day=1)
        next_month = today_date.replace(day=28) + timedelta(days=4)
        last_date = next_month - timedelta(days=next_month.day)

        # Fetch monthly entries & customer account
        # Note: Using .get() is fine, but ensure these records always exist for a customer!
        customer_daily_entry = customer_daily_entry_monthly.objects.get(customer=pk)
        coolers_total = customer_daily_entry.coolers
        customer_account = CustomerAccount.objects.get(customer_name=pk)

        # Bill number logic
        bill_number = bill_number_generator()
        last_four_digits = bill_number[-4:]
        new_last_four_digits = str(int(last_four_digits) + 1).zfill(4)
        new_bill_number = bill_number[:-4] + new_last_four_digits

        with transaction.atomic():
            # Create Bill
            CustomerBill.objects.create(
                bill_number=str(new_bill_number),
                customer_name=customer,
                from_date=first_date,
                to_date=last_date,
                coolers=coolers_total,
                Rate=int(customer.rate),
                Amount=int(coolers_total) * int(customer.rate),
                Pending_amount=int(customer_account.due),
                Advanced_amount=0,
                Total=(int(coolers_total) * int(customer.rate)) + int(customer_account.due),
                addedby=request.user.username,
            )

            # Update customer account
            customer_account.due = (int(coolers_total) * int(customer.rate)) + int(customer_account.due)
            customer_account.save()

            # Reset monthly coolers
            customer_daily_entry.coolers = 0
            customer_daily_entry.save()

        return Response({"message": "Customer Bill Generated"}, status=status.HTTP_201_CREATED)



# -----------------------------------------------------------------------
# Scheduled Task Endpoints (Called by QStash)
# -----------------------------------------------------------------------
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .task import dispatch_monthly_bill_batches, process_bill_batch_core

logger = logging.getLogger(__name__)


@csrf_exempt
def run_monthly_bill_task(request):
    """
    DISPATCHER — Called by QStash cron daily at 23:00.
    Delegates all fan-out logic to dispatch_monthly_bill_batches() in task.py.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    result = dispatch_monthly_bill_batches()

    if result.get("skipped"):
        return JsonResponse({"status": "skipped", "message": result["message"]}, status=200)

    return JsonResponse({"status": "success", **result})


@csrf_exempt
def process_bill_batch(request):
    """
    WORKER — Called by QStash for each batch the Dispatcher enqueued.
    Parses the payload and delegates processing to process_bill_batch_core() in task.py.

    Payload: { "customer_ids": [...], "first_date": "YYYY-MM-DD", "last_date": "YYYY-MM-DD" }
    Returns 500 on failure so QStash automatically retries the batch.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
        customer_ids = body["customer_ids"]
        first_date = body["first_date"]
        last_date = body["last_date"]
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("process_bill_batch view: bad payload — %s", exc)
        return JsonResponse({"error": f"Invalid payload: {exc}"}, status=400)

    try:
        process_bill_batch_core(customer_ids, first_date, last_date)
    except Exception as exc:
        logger.error("process_bill_batch view: batch failed — %s", exc, exc_info=True)
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({"status": "success", "processed": len(customer_ids)})
