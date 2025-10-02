from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import yaml

schema_view = get_schema_view(
    openapi.Info(
        title="Banas API",
        default_version="v1",
        description="Your API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)
