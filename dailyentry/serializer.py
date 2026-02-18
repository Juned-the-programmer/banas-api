from rest_framework import serializers

from .models import DailyEntry, pending_daily_entry


# For create/update DailyEntry
class DailyEntrySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)

    class Meta:
        model = DailyEntry
        fields = ["id", "customer", "customer_name", "cooler", "date_added", "addedby", "updatedby"]
        read_only_fields = ["id", "customer_name", "addedby", "updatedby"]


# For single record retrieval
class DailyEntrySerializerGETSingle(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)

    class Meta:
        model = DailyEntry
        fields = ["id", "customer", "cooler", "date_added", "addedby", "updatedby", "customer_name"]


# For Dashboard lightweight fetch
class DailyEntrySerializerGETDashboard(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = ["cooler", "date_added", "addedby"]


# For bulk import
class DailyEntryBulkImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = ["customer", "cooler"]  # only required fields


# Pending daily entries
class PendingDailyEntrySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)

    class Meta:
        model = pending_daily_entry
        fields = ["id", "customer", "coolers", "date_added", "customer_name"]


# Verify result serializer
class DailyEntryVerifyResultSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=50, required=True)
    customer = serializers.CharField(max_length=50, required=True)
    coolers = serializers.IntegerField(required=True)
    date_added = serializers.DateTimeField(required=True)
