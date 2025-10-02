from rest_framework import serializers

from bills.models import CustomerBill
from dailyentry.models import DailyEntry, customer_qr_code
from globalserializers import CustomeDateField
from payment.models import CustomerPayment
from route.models import Route

from .models import Customer, CustomerAccount


class CustomerSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), many=False)
    date_added = CustomeDateField()
    date_updated = CustomeDateField()

    class Meta:
        model = Customer
        fields = "__all__"


class CustomerSerializerList(serializers.ModelSerializer):
    date_added = CustomeDateField()
    date_updated = CustomeDateField()
    route = serializers.StringRelatedField()

    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "phone_no", "route", "active", "date_added", "date_updated"]


## Nested Serializers ##


class CustomerAccountSerializer(serializers.ModelSerializer):
    date = CustomeDateField()

    class Meta:
        model = CustomerAccount
        fields = "__all__"


class CustomerAccountNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAccount
        fields = ["total_paid", "due"]


class CustomerQRNestedSerializer(serializers.ModelSerializer):
    qrcode_url = serializers.SerializerMethodField()

    class Meta:
        model = customer_qr_code
        fields = ["qrcode_url"]

    def get_qrcode_url(self, obj):
        return obj.qrcode.url


class CustomerBillNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = ["bill_number", "from_date", "to_date", "coolers", "Total", "paid", "id"]


class CustomerDailyEntryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = ["cooler", "date_added", "addedby"]


class CustomerPaymentNestedSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomerPayment
        fields = ["id", "customer_name", "pending_amount", "paid_amount", "date", "addedby", "rounf_off_amount"]

    def get_customer_name(self, obj):
        return f"{obj.customer_name.first_name} {obj.customer_name.last_name}"


# Main customer serializer
class CustomerDetailNestedSerializer(serializers.ModelSerializer):
    customer_account = CustomerAccountNestedSerializer()
    route = serializers.StringRelatedField()
    daily_entry_monthly = serializers.SerializerMethodField()
    qr_code = CustomerQRNestedSerializer(source="customer_qr_code", read_only=True)
    bills = CustomerBillNestedSerializer(source="customer_bill", many=True)
    daily_entries = CustomerDailyEntryNestedSerializer(source="customer_daily_entry", many=True)
    payments = CustomerPaymentNestedSerializer(source="customer_payment", many=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "sequence_no",
            "phone_no",
            "route",
            "rate",
            "date_added",
            "active",
            "customer_account",
            "bills",
            "daily_entries",
            "daily_entry_monthly",
            "payments",
            "qr_code",
        ]

    def get_daily_entry_monthly(self, obj):
        # Handles missing object gracefully
        return getattr(obj.customer_daily_entry_monthly, "coolers", 0)
