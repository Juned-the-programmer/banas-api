from rest_framework import serializers

from globalserializers import CustomeDateField

from .models import *


class CustomerPaymentSerializer(serializers.ModelSerializer):
    date = CustomeDateField()

    class Meta:
        model = CustomerPayment
        fields = "__all__"


class CustomerPaymentSerializerGET(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    date = CustomeDateField()

    class Meta:
        model = CustomerPayment
        fields = ["customer_name", "pending_amount", "paid_amount", "date", "addedby", "rounf_off_amount"]

    def get_customer_name(self, obj):
        return f"{obj.customer_name.first_name} {obj.customer_name.last_name}"
