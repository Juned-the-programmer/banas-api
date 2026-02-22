import os

from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from banas.cache_conf import customer_cached_data, total_pending_due_cached
from dailyentry.models import DailyEntry_dashboard

from .serializer import CustomTokenObtainPairSerializer

# Create your views here.


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    token_obtain_pair = TokenObtainPairView.as_view()


@api_view(["GET"])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_qr_codes(request):
    qr_folder = settings.MEDIA_ROOT  # /media/qr_codes/files
    files_list = []

    if os.path.exists(qr_folder):
        # Only list files (skip directories like lost+found)
        files_list = [
            request.build_absolute_uri(settings.MEDIA_URL + f)
            for f in os.listdir(qr_folder)
            if os.path.isfile(os.path.join(qr_folder, f))
        ]

    return JsonResponse({"files": files_list})


@api_view(["GET"])
@permission_classes([IsAdminUser, IsAuthenticated])
def dashboard(request):
    # Active customer count — derived from the cached customer queryset (no DB hit)
    customers = customer_cached_data()
    total_active_customers = sum(1 for c in customers if c.active)

    # Today's delivery counters — direct ORM (single-row table, very cheap)
    dashboard_record = DailyEntry_dashboard.objects.first()
    today_customer_count = dashboard_record.customer_count if dashboard_record else 0
    today_coolers_count = dashboard_record.coolers_count if dashboard_record else 0

    # Total outstanding due — cached, refreshes every 5 min
    total_pending_due = total_pending_due_cached()

    return JsonResponse(
        {
            "total_active_customers": total_active_customers,
            "today_customer_count": today_customer_count,
            "today_coolers_count": today_coolers_count,
            "total_pending_due": total_pending_due,
        },
        status=status.HTTP_200_OK,
    )



@api_view(["GET"])
@permission_classes([IsAdminUser, IsAuthenticated])
def get_profile(request):
    user = User.objects.get(username=request.user.username)

    return JsonResponse(
        {
            "username": user.username,
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.first_name + " " + user.last_name,
            "is_superuser": user.is_superuser,
            "email": user.email or "",  # Handle empty email
        },
        status=status.HTTP_200_OK,
    )

