from django.urls import path

from . import views
from .qstah import task_verify_pending_daily_entries, task_bulk_import_daily_entries

urlpatterns = [
    # CBVs for daily entry
    path("", views.DailyEntryListCreateView.as_view(), name="daily-entry"),
    path("<str:pk>/", views.DailyEntryDetailUpdateDeleteView.as_view(), name="view_delete_daily_entry"),
    path("count/today/", views.DailyEntryCountView.as_view(), name="daily-entry-count"),
    path("bulk/import/", views.DailyEntryBulkImportView.as_view(), name="daily_entry_bulk"),
    path("verify/dailyentry/", views.VerifyPendingDailyEntryView.as_view(), name="verify_pending_daily_entry"),
    path("list/pending/dailyentry/", views.PendingDailyEntryListView.as_view(), name="list_pending_daily_entry"),
    path("today/missing/", views.MissingDailyEntryView.as_view(), name="missing_daily_entry"),
    # FBVs for QR and historical (still required)
    path("customer/dailyentry/<str:pk>", views.customer_qr_daily_entry, name="customer_qr_daily_entry_no_slash"),
    path("customer/dailyentry/<str:pk>/", views.customer_qr_daily_entry, name="customer_qr_daily_entry"),
    # Scheduled task endpoints (called by QStash)
    path("tasks/reset-dashboard/", views.run_reset_dashboard_task, name="reset-dashboard-task"),
    # Async task endpoints (called by QStash)
    path("tasks/verify-pending/", task_verify_pending_daily_entries, name="task-verify-pending"),
    path("tasks/bulk-import/", task_bulk_import_daily_entries, name="task-bulk-import"),
]
