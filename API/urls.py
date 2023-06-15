from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
)

urlpatterns = [
  path('login/', views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
  path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('user/get-profile/', views.get_profile, name='get_profile'),
  path('dashboard/', views.dashboard, name="dashboard"),
]

