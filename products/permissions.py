from rest_framework.permissions import BasePermission

class IsCustomerOrNone(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return True
    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous:
            if request.user.groups.filter(name='customers').exists():
                return True
        return False


class IsSellerOrNone(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            if request.user.groups.filter(name='sellers').exists():
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous:
            if request.user.groups.filter(name='sellers').exists():
                return True
        return False
