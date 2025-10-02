from django.urls import path

from . import views

urlpatterns = [
    path('', views.RouteListCreateView.as_view()),
    path('<str:pk>/', views.RouteRetrieveUpdateView.as_view() , name="list_update_route")
]
