from rest_framework import permissions, viewsets
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist

from time_tracking.work_time.models import WorkTime, convert_time_to_unix
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

    def create(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().filter(
                unix_end_time__isnull=True
            ).get()
        except DoesNotExist:
            return Response(
                {"detail": _("Bad request you are not checked in")},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        time_now = timezone.now()
        instance.unix_end_time = convert_time_to_unix(time_now)
        instance

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkTimeCheckInViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    """
    This viewset provides `list` and `create` actions for all the users
    """
    serializer_class = WorkTimeCheckInSerializer

    def create(self, request, *args, **kwargs):
        is_instance_exists = self.get_queryset().filter(
            unix_end_time__isnull=True).exists()

        if is_instance_exists is False:
            return super().create(request, *args, **kwargs)

        return Response(
            {"detail": _("Bad request you are already checked in")},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
