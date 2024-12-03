from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Разрешение, которое позволяет редактировать или удалять видео только владельцу
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user_id
