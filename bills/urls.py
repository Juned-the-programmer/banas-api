from django.urls import path
from . import views

urlpatterns = [
    path('bills/', views.get_bills, name="get-bills"),
    path('<str:pk>/', views.bill_detail, name="bill-detail"),
    path('generatebill/<str:pk>/', views.generate_bill, name="generate-bill")
]
