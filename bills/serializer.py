from rest_framework import serializers
from .models import *

class GenerateBillSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomerBill
    fields = '__all__'


class GenerateBillSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = CustomerBill
    fields = '__all__'
    depth = 1


class DetailBillSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomerBill
    fields = ['bill_number', 'from_date', 'to_date', 'coolers', 'Total', 'paid', 'id']