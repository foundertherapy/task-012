from datetime import date
from django.db.models import Sum, F
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from time_tracking.event.models import Event
from time_tracking.vacation.models import Vacation
from time_tracking.vacation.permissions import IsOwner
from time_tracking.vacation.serializers import VacationSerializer


class VacationViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `detail`, `create`,
    `update`, and `delete` for all users.
    """
    serializer_class = VacationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Vacation.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vacations = Vacation.objects.filter(
            owner=self.request.user,
            start_date__gte=date(timezone.now().year, 1, 1),
        ).aggregate(sum=Sum(1 + F('end_date') - F('start_date')))

        if vacations['sum'] is not None:
            if vacations['sum'].days >= 16:
                return Response(
                    {"detail": _("Reached max vacations days")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            requested_vacation_days = 1 + (
                    serializer.validated_data['end_date']
                    - serializer.validated_data['start_date']
            ).days
            remaining_days = 16 - vacations['sum'].days
            if remaining_days - requested_vacation_days < 0:
                return Response(
                    {"detail": _("Can't add more than %(days)s") % {
                        'days': remaining_days
                    }},
                    status=status.HTTP_400_BAD_REQUEST
                )

        events_intersection = Event.objects.filter(
            end_date__gte=serializer.validated_data['start_date']
        ).filter(
            start_date__lte=serializer.validated_data['end_date']
        ).exclude(
            start_date__gt=serializer.validated_data['end_date']
        ).exclude(
            end_date__lt=serializer.validated_data['start_date']
        ).values('id')

        if len(events_intersection) != 0:
            return Response(
                {"detail": _("Events are intersection with your vacation"),
                 "events_urls": [(
                     request.build_absolute_uri(
                         reverse('event-detail', args=[event['id']])
                     ) for event in events_intersection
                 )]},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.start_date < timezone.now().date():
            return Response(
                {"detail": _("You can't delete old vacation dates")},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
