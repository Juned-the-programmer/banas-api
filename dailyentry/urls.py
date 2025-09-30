from django.urls import path
from . import views

urlpatterns = [
    # CBVs for daily entry
    path('', views.DailyEntryListCreateView.as_view(), name="daily-entry"),
    path('<str:pk>/', views.DailyEntryDetailUpdateDeleteView.as_view(), name="view_delete_daily_entry"),
    path('count/today/', views.DailyEntryCountView.as_view(), name="daily-entry-count"),
    path('bulk/import/', views.DailyEntryBulkImportView.as_view(), name="daily_entry_bulk"),
    path('verify/dailyentry/', views.VerifyPendingDailyEntryView.as_view(), name="verify_pending_daily_entry"),
    path('list/pending/dailyentry/', views.PendingDailyEntryListView.as_view(), name="list_pending_daily_entry"),

    # FBVs for QR and historical (still required)
    path('customer/dailyentry/<str:pk>/', views.customer_qr_daily_entry, name="customer_qr_daily_entry"),
    path('historical/', views.historical_data_retriever, name="historical_data_retriever"),
]