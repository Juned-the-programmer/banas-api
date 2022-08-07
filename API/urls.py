from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('user/token/',TokenObtainPairView.as_view(),name="token_obtain_pair"),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
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
    path('due-list/<str:pk>/',views.due_list, name="due_list"),
    path('customer-due/<str:pk>/',views.due_customer,name="customer-due"),
    path('customer-detail/<str:pk>/',views.customer_detail,name="customer-detail"),
    path('bill-detail/<str:pk>/',views.bill_detail,name="bill-detail")
]   
