from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name="login"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('add-route/',views.add_route,name="add-route"),
    path('add-customer/',views.add_customer,name="add-customer"),
    path('update-customer/<str:pk>/',views.update_customer,name="update-customer"),
    path('list-route/',views.list_route,name="list-route"),
    path('list-customer/',views.list_customer,name="list-customer"),
    path('daily-entry/',views.add_daily_entry,name="daily-entry"),
    path('daily-entry-count/',views.daily_count,name="daily-entry-count"),
    path('customer-payment/',views.customer_payment,name="customer-payment"),
    path('customer-account/<str:pk>/',views.customer_account,name="customer-account"),
    path('get-bill-data/<str:pk>/',views.get_bill_data,name="get-bill-data"),
    path('generate-bill/',views.generate_bill,name="generate-bill"),
    path('due-list/<str:pk>/',views.due_list, name="due_list"),
]
