from rest_framework import serializers
from .models import CustomerPayment
from globalserializers import CustomeDateField

# Serializer for create/update
class CustomerPaymentSerializer(serializers.ModelSerializer):
    date = CustomeDateField()
    
    class Meta:
        model = CustomerPayment
        fields = '__all__'


# Optimized GET serializer with customer name included
class CustomerPaymentSerializerGET(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer_name.get_full_name', read_only=True)
    date = CustomeDateField()
    
    class Meta:
        model = CustomerPayment
        fields = ['customer_name', 'pending_amount', 'paid_amount', 'date', 'addedby', 'rounf_off_amount']
