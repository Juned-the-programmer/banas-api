from rest_framework import serializers
from .models import *

class CustomerPaymentSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomerPayment
    fields = '__all__'


class CustomerPaymentSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = CustomerPayment
    fields = ['pending_amount', 'paid_amount', 'date', 'addedby']