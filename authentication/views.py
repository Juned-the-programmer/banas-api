import datetime
import os
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from dailyentry.models import DailyEntry

from . import serializer
from .serializer import *

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


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser, IsAuthenticated])
def dashboard(request):
    if request.method == "GET":
        today_date = datetime.date.today()

        data_list = []

        for i in range(0, 7):
            daily_entry = DailyEntry.objects.filter(date_added=today_date - timedelta(days=i)).aggregate(Sum("cooler"))
            coolers_total = daily_entry["cooler__sum"]

            if coolers_total is None:
                coolers = 0
            else:
                coolers = coolers_total

            data_list.append({"date": str(today_date - timedelta(days=i)), "coolers": coolers})

        return JsonResponse(data_list, status=status.HTTP_200_OK, safe=False)

    if request.method == "POST":
        date_data = request.data
        data_values = list(date_data.values())

        try:
            # Configuring date
            from_date = datetime.datetime.strptime(data_values[0], "%Y-%m-%d")
            to_date = datetime.datetime.strptime(data_values[1], "%Y-%m-%d")
            days = to_date - from_date

            data_list = []

            for i in range(0, int(days.days)):
                daily_entry = DailyEntry.objects.filter(date_added=to_date - timedelta(days=i)).aggregate(Sum("cooler"))
                coolers_total = daily_entry["cooler__sum"]

                if coolers_total is None:
                    coolers = 0
                else:
                    coolers = coolers_total

                data_list.append({"date": str(to_date - timedelta(days=i)), "coolers": coolers})

            return JsonResponse(data_list, status=status.HTTP_200_OK, safe=False)

        except:
            return JsonResponse({"message": "Something went wrong, Please try again!"}, status=status.HTTP_400_BAD_REQUEST)


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
            "email": user.email,
        },
        status=status.HTTP_200_OK,
    )
