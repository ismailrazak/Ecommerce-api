from rest_framework.permissions import BasePermission


class IsTheSameUserOrNone(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous:
            if request.user == obj:
                return True
        return False
