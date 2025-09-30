from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomerListView.as_view()),
    path('route/<str:pk>/', views.CustomerByRouteView.as_view(), name="list-customer-route"),
    path('<str:pk>/', views.CustomerDetialUpdateView.as_view()),
    path('account/<str:pk>/', views.CustomerAccountUpdateView.as_view(), name="customer-account"),
    path('detail/<str:pk>/', views.CustomerDetailView.as_view(), name="customer-detail")
]
