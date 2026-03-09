from django.conf import settings
from django.urls import path

from .views import BackupView, RestoreView

_restore_path = getattr(settings, "RESTORE_PATH", "restore-db")

urlpatterns = [
    path("", BackupView.as_view(), name="backup"),
    path(f"{_restore_path}/", RestoreView.as_view(), name="restore"),
]
