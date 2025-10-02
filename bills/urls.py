from django.urls import path
from .views import BillListView, BillDetailView, GenerateBillView

urlpatterns = [
    path('bills/', BillListView.as_view(), name="get-bills"),
    path('<str:pk>/', BillDetailView.as_view(), name="bill-detail"),
    path('generatebill/<str:pk>/', GenerateBillView.as_view(), name="generate-bill"),
]
