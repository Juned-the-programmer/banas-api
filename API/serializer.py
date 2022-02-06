from rest_framework import serializers
from .models import *


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Customer
        fields ='__all__'

class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = '__all__'