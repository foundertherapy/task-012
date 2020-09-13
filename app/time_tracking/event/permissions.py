from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffMemberOrReadOnly(BasePermission):
    """
    Allow only staff members to edit/create/update/delete while read
    permissions "GET, HEAD or OPTIONS requests" are allowed to any request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff is True
        )
