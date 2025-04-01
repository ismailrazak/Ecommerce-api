from rest_framework.permissions import BasePermission


class IsTheSameUserOrNone(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous:
            if request.user == obj:
                return True
        return False
