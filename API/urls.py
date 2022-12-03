from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/',views.CustomTokenObtainPairView.as_view(),name="token_obtain_pair"),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/get-profile',views.get_profile,name='get_profile'),

    path('dashboard/',views.dashboard,name="dashboard"),

    path('add-route/',views.add_route,name="add-route"),
    path('list-route/',views.list_route,name="list-route"),
    path('update-route/<str:pk>/',views.update_route,name="update-route"),
    
    path('add-customer/',views.add_customer,name="add-customer"),
    path('update-customer/<str:pk>/',views.update_customer,name="update-customer"),
    path('customer-info/<str:pk>/',views.get_customer_detail,name="customer-info"),
    path('list-customer/',views.list_customer,name="list-customer"),
    path('customer-account/<str:pk>/',views.customer_account,name="customer-account"),
    path('customer-due/<str:pk>/',views.due_customer,name="customer-due"),
    path('customer-detail/<str:pk>/',views.customer_detail,name="customer-detail"),

    path('customer-payment/',views.customer_payment,name="customer-payment"),
    path('customer-payment-list/<str:pk>/',views.cutomer_payment_list,name="customer-payment-list"),
    path('customer-payment-current-month/',views.customer_payment_current_month,name="customer-payment-current-month"),
    path('payment-list-route/<str:pk>/',views.payment_list_route,name="payment-list-route"),
    path('due-list-route/<str:pk>/',views.due_list_route, name="due_list_route"),
    path('due-list/',views.due_list,name="due_list"),
    path('bill-detail/<str:pk>/',views.bill_detail,name="bill-detail"),

    path('daily-entry/',views.add_daily_entry,name="daily-entry"),
    path('daily-entry-count/',views.daily_count,name="daily-entry-count"),
]   
