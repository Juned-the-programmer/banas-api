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

    path('route/',views.route,name="add-route"),
    path('update-route/<str:pk>/',views.update_route,name="update-route"),
    
    path('customer/',views.customer,name="add-customer"),
    path('customer/route/<str:pk>/',views.list_customer_by_route,name="list-customer-route"),
    path('update-customer/<str:pk>/',views.update_customer,name="update-customer"),
    path('customer/info/<str:pk>/',views.get_customer_detail,name="customer-info"),
    path('customer/account/<str:pk>/',views.customer_account,name="customer-account"),
    path('customer/due/<str:pk>/',views.due_customer,name="customer-due"),
    path('customer/detail/<str:pk>/',views.customer_detail,name="customer-detail"),

    path('payment/',views.payment,name="customer-payment"),
    path('customer/payment/<str:pk>/',views.cutomer_payment_list,name="customer-payment-list"),
    path('payment/route/<str:pk>/',views.payment_list_route,name="payment-list-route"),
    path('due/route/<str:pk>/',views.due_list_route, name="due_list_route"),
    path('due/',views.due_list,name="due_list"),
    path('bill/<str:pk>/',views.bill_detail,name="bill-detail"),

    path('daily-entry/',views.daily_entry,name="daily-entry"),
]   
