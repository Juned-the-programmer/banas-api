from rest_framework import serializers

from .models import *


class GenerateBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = "__all__"


class GenerateBillSerializerGET(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomerBill
        fields = "__all__"

    def get_customer_name(self, obj):
        return f"{obj.customer_name.first_name} {obj.customer_name.last_name}"


class DetailBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = ["bill_number", "from_date", "to_date", "coolers", "Total", "paid", "id"]
