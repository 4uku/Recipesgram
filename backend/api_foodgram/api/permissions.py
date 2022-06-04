from rest_framework.permissions import SAFE_METHODS, BasePermission


class AnonOrAuthOrAuthor(BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        return request.method in SAFE_METHODS or request.user == obj.author
