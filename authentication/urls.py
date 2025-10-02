from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/get-profile/", views.get_profile, name="get_profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("list-qr-codes/", views.list_qr_codes, name="list_qr_codes"),
]
