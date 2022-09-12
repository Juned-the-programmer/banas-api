from rest_framework import serializers
from .models import *


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):    
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(),many=False)
    # route = RouteSerializer(read_only=True)
    class Meta:
        model = Customer
        fields ='__all__'

class CustomerSerializerGET(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'
        depth = 1

class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = '__all__'

class CustomerPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPayment
        fields = '__all__'

class CustomerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAccount
        fields = '__all__'


class GenerateBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = '__all__'