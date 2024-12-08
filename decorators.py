from rest_framework.permissions import IsAdminUser, IsAuthenticated

class IsAdmin_or_staff_user(IsAdminUser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        return request.user.is_staff