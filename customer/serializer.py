from rest_framework import serializers
from .models import *
from route.serializers import RouteSerializerGET
from globalserializers import CustomeDateField

class CustomerSerializer(serializers.ModelSerializer):
  route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), many=False)
  date_added = CustomeDateField()
  date_updated = CustomeDateField()
  class Meta:
    model = Customer
    fields = '__all__'


class CustomerSerializerList(serializers.ModelSerializer):
  date_added = CustomeDateField()
  date_updated = CustomeDateField()
  route = serializers.StringRelatedField()
  class Meta:
    model = Customer
    fields = '__all__'


class CustomerSerializerGET(serializers.ModelSerializer):
  date_added = CustomeDateField()
  date_updated = CustomeDateField()
  route = RouteSerializerGET()
  class Meta:
    model = Customer
    fields = '__all__'
    depth = 1
    
class CustomerAccountSerializer(serializers.ModelSerializer):
  date = CustomeDateField()
  class Meta:
    model = CustomerAccount
    fields = '__all__'


class CustomerAccountSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = CustomerAccount
    fields = ['customer_name', 'due']
    depth = 1