from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment, name="customer-payment"),
    path('customer/<str:pk>/', views.cutomer_payment_list, name="customer-payment-list"),
    path('route/<str:pk>/', views.payment_list_route, name="payment-list-route"),
    path('due/route/<str:pk>/', views.due_list_route, name="due_list_route"),
    path('due/', views.due_list, name="due_list"),
]
