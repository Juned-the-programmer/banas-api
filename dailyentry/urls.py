from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_entry, name="daily-entry"),
    path('historical/' , views.historical_data_retriever, name="historical_data_retriever"),
    path('<str:pk>/', views.view_delete_daily_entry, name="view_delete_daily_entry"),
    path('count/today', views.daily_entry_count, name="daily-entry-count"),
    path('bulk/import/',views.daily_entry_bulk, name="daily_entry_bulk"),
    path('verify/dailyentry/', views.verify_pending_daily_entry, name="verify_pending_daily_entry"),
    path('list/pending/dailyentry/', views.list_pending_daily_entry, name="list_pending_daily_entry"),
    path('customer/dailyentry/<str:pk>', views.customer_qr_daily_entry, name="customer_qr_daily_entry"),
]
