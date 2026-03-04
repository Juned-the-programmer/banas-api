from django.urls import path

from . import views
from .qstash import task_generate_qr, task_send_email, task_send_whatsapp

urlpatterns = [
    path("", views.CustomerListView.as_view()),
    path("route/<str:pk>/", views.CustomerByRouteView.as_view(), name="list-customer-route"),
    path("<str:pk>/", views.CustomerDetialUpdateView.as_view()),
    path("account/<str:pk>/", views.CustomerAccountUpdateView.as_view(), name="customer-account"),
    path("detail/<str:pk>/", views.CustomerDetailView.as_view(), name="customer-detail"),
    # Async task endpoints (called by QStash)
    path("tasks/send-email/", task_send_email, name="task-send-email"),
    path("tasks/generate-qr/", task_generate_qr, name="task-generate-qr"),
    path("tasks/send-whatsapp/", task_send_whatsapp, name="task-send-whatsapp"),
]
