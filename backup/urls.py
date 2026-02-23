from django.urls import path

from .views import BackupView, RestoreView

urlpatterns = [
    path("", BackupView.as_view(), name="backup"),
    path("restore/", RestoreView.as_view(), name="restore"),
]
