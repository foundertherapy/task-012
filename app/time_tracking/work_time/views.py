from rest_framework import permissions, viewsets

from time_tracking.work_time.models import WorkTime
from time_tracking.work_time.serializers import WorkTimeSerializer


class WorkTimeViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `detail`, `create`,
    `update`, and `delete` for all users.
    """
    serializer_class = WorkTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkTime.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
