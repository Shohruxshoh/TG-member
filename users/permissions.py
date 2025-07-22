from rest_framework.permissions import BasePermission

class IsAdminStaff(BasePermission):
    """
    Foydalanuvchi is_staff bo'lsa, unga ruxsat beriladi.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
