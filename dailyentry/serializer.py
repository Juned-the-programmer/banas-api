from rest_framework import serializers
from .models import DailyEntry, pending_daily_entry
from customer.models import *
import uuid

class DailyEntrySerializer(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'


class DailyEntrySerializerGET(serializers.ModelSerializer):
  customer_name = serializers.SerializerMethodField()
  class Meta:
    model = DailyEntry
    fields = ['id','cooler','date_added','addedby','updatedby','customer_name']

  def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"


class DailyEntrySerializerGETSingle(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'


class DialyEntrySerializerGETDashboard(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = ['cooler', 'date_added', 'addedby']
    
class DailyEntryBulkImportSerializer(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'

class Pending_Daily_Entry_Serializer(serializers.ModelSerializer):
  customer_name = serializers.SerializerMethodField()
  class Meta:
    model = pending_daily_entry
    fields = '__all__'

  def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"

class DailyEntry_Verify_Result_Serializer(serializers.Serializer):
  pendng_id = models.CharField(max_length=50, null=True, blank=True)
  customer = models.CharField(max_length=50, null=True, blank=True)
  cooler = models.IntegerField(default=0, null=True, blank=True)
  date_added = models.DateTimeField(null=True, blank=True)