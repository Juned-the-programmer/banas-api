from rest_framework import serializers
from .models import *

class RouteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Route
    fields = '__all__'


class RouteSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = Route
    fields = '__all__'
    depth = 1