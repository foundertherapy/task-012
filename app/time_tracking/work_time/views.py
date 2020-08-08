from rest_framework import permissions, viewsets
from django.utils import timezone

from time_tracking.work_time.models import WorkTime
from rest_framework import mixins, generics, status
from rest_framework.response import Response
from time_tracking.work_time.serializers import (
    WorkTimeSerializer,
    WorkTimeCheckInSerializer,
    WorkTimeCheckOutSerializer
)


class WorkTimeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset provides `list` and `detail` actions for all the users
    """
    serializer_class = WorkTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkTime.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GenericViewSet(viewsets.ViewSetMixin, generics.GenericAPIView):
    """
    Generic class to containe the permissions and
    the `get_queryset` method
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkTime.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WorkTimeCheckOutViewSet(mixins.ListModelMixin,
                              GenericViewSet):
    """
    This viewset provides `list` and `create` actions for all the users
    """
    serializer_class = WorkTimeCheckOutSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None or instance.end_time is not None:
            return Response(
                {"detail": "Bad request you are not checked in"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data)
        instance.end_time = timezone.now()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkTimeCheckInViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    """
    This viewset provides `list` and `create` actions for all the users
    """
    serializer_class = WorkTimeCheckInSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None or instance.end_time is not None:
            return super().create(request, *args, **kwargs)
        return Response(
            {"detail": "Bad request you are alrady checked in"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
