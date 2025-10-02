from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from exception.views import route_not_found_exception

from .models import Route
from .serializers import RouteSerializer, RouteSerializerGET


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
