from rest_framework import permissions


class IsStaffMemberOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff members to edit/create/update/delete.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions "GET, HEAD or OPTIONS requests" are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to staff members.
        return True == request.user.is_staff
