from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomerListView.as_view()),
    path('route/<str:pk>/', views.list_customer_by_route, name="list-customer-route"),
    path('<str:pk>/', views.Customer_detail_view_update),
  # path('<str:pk>/',views.get_customer_detail,name="customer-info"),
    path('account/<str:pk>/', views.customer_account, name="customer-account"),
    path('due/<str:pk>/', views.due_customer, name="customer-due"),
    path('detail/<str:pk>/', views.customer_detail, name="customer-detail"),
]
