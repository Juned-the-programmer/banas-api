from rest_framework import serializers
from .models import *
from rest_framework.exceptions import ValidationError

class RouteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Route
    fields = ['route_name']

  def validate_route_name(self, value):
    if Route.objects.filter(route_name=value).exists():
      raise ValidationError("Route already Exists")
    return value

class RouteSerializerGET(serializers.ModelSerializer):
  class Meta:
    model = Route
    fields = '__all__'
    depth = 1