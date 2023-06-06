from django.urls import path
from . import views

urlpatterns = [
    path('', views.RouteListView),
    path('<str:pk>/', views.list_update_route , name="list_update_route")
]
