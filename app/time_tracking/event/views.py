from rest_framework import permissions, viewsets

from time_tracking.event.models import Event
from time_tracking.event.permissions import IsStaffMemberOrReadOnly
from time_tracking.event.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list` and `detail` actions for all the users
    and provides `create`, `update`, and `delete` for the staff members
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsStaffMemberOrReadOnly
    ]
