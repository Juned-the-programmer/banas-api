from django.urls import path

from .views import BillDetailView, BillListView, GenerateBillView, RenderBillView, process_bill_batch, run_monthly_bill_task

urlpatterns = [
    path("bills/", BillListView.as_view(), name="get-bills"),
    path("<str:pk>/", BillDetailView.as_view(), name="bill-detail"),
    path("generatebill/<str:pk>/", GenerateBillView.as_view(), name="generate-bill"),
    path("invoice/<str:pk>/", RenderBillView.as_view(), name="render-bill"),
    # Scheduled task endpoints (called by QStash)
    path("tasks/monthly-bill-check/", run_monthly_bill_task, name="monthly-bill-task"),
    path("tasks/process-bill-batch/", process_bill_batch, name="process-bill-batch"),
]
