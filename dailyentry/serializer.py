from rest_framework import serializers

from .models import DailyEntry, pending_daily_entry


# For create/update DailyEntry
class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = ["id", "customer", "cooler", "date_added", "addedby", "updatedby"]
        read_only_fields = ["id", "addedby", "updatedby"]


# For list DailyEntries (with customer_name)
class DailyEntrySerializerGET(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)

    class Meta:
        model = DailyEntry
        fields = ["id", "cooler", "date_added", "addedby", "updatedby", "customer_name"]


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


# Verify result serializer (FIXED)
class DailyEntryVerifyResultSerializer(serializers.Serializer):
    pending_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    customer = serializers.CharField(max_length=50, required=False, allow_blank=True)
    cooler = serializers.IntegerField(required=False)
    date_added = serializers.DateTimeField(required=False)
