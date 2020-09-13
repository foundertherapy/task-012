from rest_framework import viewsets

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
    permission_classes = [IsStaffMemberOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
