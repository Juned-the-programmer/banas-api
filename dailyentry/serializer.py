from rest_framework import serializers
from .models import DailyEntry
from customer.models import *

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