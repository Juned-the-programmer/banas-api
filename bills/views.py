import datetime
import pytz

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from customer.models import Customer, CustomerAccount
from dailyentry.models import customer_daily_entry_monthly
from dailyentry.serializer import DailyEntrySerializerGETDashboard

from .models import CustomerBill
from .serializer import GenerateBillSerializer, GenerateBillSerializerGET
from .task import bill_number_generator
from .utils import get_dynamic_entries
from exception.views import customer_not_found_exception

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

        if not bill.from_date_as_date or not bill.to_date_as_date:
            return Response({"error": "Invalid date format in bill"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare dynamic daily entries
        from_date = bill.from_date
        to_date = bill.to_date

        from_date_new = datetime.datetime.combine(
        bill.from_date_as_date, 
        datetime.time.min).replace(tzinfo=pytz.UTC)
    
        to_date_new = datetime.datetime.combine(
        bill.to_date_as_date, 
        datetime.time.max).replace(tzinfo=pytz.UTC)

        # Determine table name for historical data
        table_name = f"DailyEntry_{bill.bill_month.strftime('%B_%Y')}"

        raw_data = get_dynamic_entries(bill.customer_name.id, from_date_new, to_date_new, table_name)
        daily_entry_serializer = DailyEntrySerializerGETDashboard(raw_data, many=True)

        return Response({
            "bill": GenerateBillSerializerGET(bill).data,
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

        # Calculate date range
        next_month = today_date.replace(day=28) + timedelta(days=4)
        last_date = next_month - timedelta(days=next_month.day)
        first_date = today_date.replace(day=1).date()

        # Fetch monthly entries & customer account
        customer_daily_entry = customer_daily_entry_monthly.objects.get(customer=pk)
        coolers_total = customer_daily_entry.coolers
        customer_account = CustomerAccount.objects.get(customer_name=pk)

        # Bill number logic
        bill_number = bill_number_generator()
        last_four_digits = bill_number[-4:]
        new_last_four_digits = str(int(last_four_digits) + 1).zfill(4)
        new_bill_number = bill_number[:-4] + new_last_four_digits

        # Create Bill
        CustomerBill.objects.create(
            bill_number=str(new_bill_number),
            customer_name=customer,
            from_date=str(first_date),
            to_date=str(last_date.date()),
            coolers=coolers_total,
            Rate=int(customer.rate),
            Amount=int(coolers_total) * int(customer.rate),
            Pending_amount=int(customer_account.due),
            Advanced_amount=0,
            Total=(int(coolers_total) * int(customer.rate)) + int(customer_account.due),
            addedby=request.user.username
        )

        # Update customer account
        customer_account.due = (int(coolers_total) * int(customer.rate)) + int(customer_account.due)
        customer_account.save()

        # Reset monthly coolers
        customer_daily_entry.coolers = 0
        customer_daily_entry.save()

        return Response({"message": "Customer Bill Generated"}, status=status.HTTP_201_CREATED)
