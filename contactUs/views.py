from rest_framework import generics, status
from rest_framework.response import Response

from .models import Contact
from .serializer import ContactSerializer


# -------------------------------
# List all contacts & create new contact
# -------------------------------
class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Contact form submitted successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED
        )


# -------------------------------
# Retrieve, Update, Delete a single contact
# -------------------------------
class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    lookup_field = "pk"
