from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListCreateView.as_view(), name="customer-payment"),
    path('customer/<str:pk>/', views.CustomerPaymentListView.as_view(), name="customer-payment-list"),
    path('route/<str:pk>/', views.PaymentListByRouteView.as_view(), name="payment-list-route"),
    path('due/route/<str:pk>/', views.DueListByRouteView.as_view(), name="due-list-route"),
    path('due/', views.DueListView.as_view(), name="due-list"),
]