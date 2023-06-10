from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_entry, name="daily-entry"),
    path('<str:pk>/', views.view_delete_daily_entry, name="view_delete_daily_entry"),
    path('count/today', views.daily_entry_count, name="daily-entry-count")
]
