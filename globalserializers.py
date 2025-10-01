from rest_framework import serializers


class CustomeDateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        return value.date().isoformat()
