from rest_framework import serializers
from .models import DailyEntry, pending_daily_entry
from customer.models import *
import uuid

class DailyEntrySerializer(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'


class DailyEntrySerializerGET(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = ['id','cooler','date_added','addedby','updatedby','customer']


class DailyEntrySerializerGETSingle(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'


class DialyEntrySerializerGETDashboard(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = ['cooler', 'date_added']
    
class DailyEntryBulkImportSerializer(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'

class Pending_Daily_Entry_Serializer(serializers.ModelSerializer):
  class Meta:
    model = pending_daily_entry
    fields = '__all__'

class DailyEntry_Verify_Result_Serializer(serializers.Serializer):
  pendng_id = models.CharField(max_length=50, null=True, blank=True)
  customer = models.CharField(max_length=50, null=True, blank=True)
  cooler = models.IntegerField(default=0, null=True, blank=True)