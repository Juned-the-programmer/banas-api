from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RouteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Route
    fields = '__all__'


class RouteSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = Route
    fields = '__all__'
    #         fields = ['id', 'customer_name', 'cooler' , 'date']
    depth = 1


class CustomerSerializer(serializers.ModelSerializer):
  route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), many=False)

  # route = RouteSerializer(read_only=True)
  class Meta:
    model = Customer
    fields = '__all__'


class CustomerSerializerGET(serializers.ModelSerializer):
  #     route = RouteSerializer(read_only=True)
  class Meta:
    model = Customer
    fields = '__all__'
    depth = 1


class DailyEntrySerializer(serializers.ModelSerializer):
  customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), many=False)

  class Meta:
    model = DailyEntry
    fields = '__all__'


class DailyEntrySerializerGET(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'
    #         fields = ['id','cooler','date','addedby','updatedby']
    depth = 1


class DailyEntrySerializerGETSingle(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = '__all__'


class DialyEntrySerializerGETDashboard(serializers.ModelSerializer):
  class Meta:
    model = DailyEntry
    fields = ['cooler', 'date']


class CustomerPaymentSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomerPayment
    fields = '__all__'


class CustomerPaymentSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = CustomerPayment
    fields = ['pending_amount', 'paid_amount', 'date', 'addedby']


class CustomerAccountSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomerAccount
    fields = '__all__'


class CustomerAccountSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = CustomerAccount
    fields = ['customer_name', 'due']
    depth = 1


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
    fields = ['from_date', 'to_date', 'coolers', 'Total', 'paid']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
    data.update({'user': self.user.username})
    data.update({'id': self.user.id})
    data.update({'first_name': self.user.first_name})
    data.update({'last_name': self.user.last_name})
    data.update({'full_name': self.user.first_name + " " + self.user.last_name})
    data.update({'is_superuser': self.user.is_superuser})
    data.update({'email': self.user.email})
    return data
