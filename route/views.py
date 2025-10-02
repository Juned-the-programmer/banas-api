from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from exception.views import *

from .models import Route
from .serializers import *


# Create your views here.
class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RouteSerializer
        return RouteSerializerGET

    def perform_create(self, serializer):
        try:
            serializer.save(addedby=self.request.user.username)
        except ValidationError as e:
            raise e


class RouteRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Route.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return RouteSerializer
        return RouteSerializerGET

    def get_object(self):
        try:
            return super().get_object()
        except Route.DoesNotExist:
            raise route_not_found_exception(self.kwargs.get("pk"))

    def perform_update(self, serializer):
        try:
            serializer.save(updatedby=self.request.user.username)
        except ValidationError as e:
            raise e
