from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name="login"),
    path('add-route/',views.add_route,name="add-route"),
    path('add-customer/',views.add_customer,name="add-customer"),
    path('update-customer/<str:pk>/',views.update_customer,name="update-customer"),
    path('list-route/',views.list_route,name="list-route"),
    path('list-customer/',views.list_customer,name="list-customer"),
    path('customer-count/',views.Customer_Count,name="customer-coount"),
    path('daily-entry/',views.add_daily_entry,name="daily-entry"),
    path('daily-entry-count/',views.daily_count,name="daily-entry-count"),
]
