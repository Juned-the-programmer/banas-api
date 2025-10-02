from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update({"user": self.user.username})
        data.update({"id": self.user.id})
        data.update({"first_name": self.user.first_name})
        data.update({"last_name": self.user.last_name})
        data.update({"full_name": self.user.first_name + " " + self.user.last_name})
        data.update({"is_superuser": self.user.is_superuser})
        data.update({"email": self.user.email})
        return data
