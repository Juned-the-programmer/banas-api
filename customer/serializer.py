from rest_framework import serializers
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
  route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), many=False)
  class Meta:
    model = Customer
    fields = '__all__'


class CustomerSerializerList(serializers.ModelSerializer):
  class Meta:
    model = Customer
    fields = '__all__'
    depth = 1


class CustomerSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = Customer
    fields = '__all__'
    depth = 1