from rest_framework import serializers

from .models import *


class GenerateBillSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Customer Bills"""

    class Meta:
        model = CustomerBill
        fields = "__all__"
        read_only_fields = ["id", "date", "addedby", "updatedby"]


class GenerateBillSerializerGET(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer_name.get_full_name", read_only=True)

    class Meta:
        model = CustomerBill
        fields = "__all__"
