from django.urls import path
from . import views

urlpatterns = [
    path('<str:pk>/', views.bill_detail, name="bill-detail")
]
