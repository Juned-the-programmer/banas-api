from django.urls import path

from .views import ContactDetailView, ContactListCreateView

urlpatterns = [
    path("contacts/", ContactListCreateView.as_view(), name="contact-list-create"),
    path("contacts/<uuid:pk>/", ContactDetailView.as_view(), name="contact-detail"),
]
