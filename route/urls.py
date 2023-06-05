from django.urls import path
from . import views

urlpatterns = [
    path('route/', views.RouteListView),
    path('route/<str:pk>/', views.list_update_route , name="list_update_route")
]
