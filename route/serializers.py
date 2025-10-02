from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from globalserializers import CustomeDateField

from .models import Route


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["route_name"]

    def validate_route_name(self, value):
        # Prevent duplicates except for self during update
        qs = Route.objects.filter(route_name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Route already Exists")
        return value


class RouteSerializerGET(serializers.ModelSerializer):
    date_added = CustomeDateField()
    date_updated = CustomeDateField()

    class Meta:
        model = Route
        fields = "__all__"
