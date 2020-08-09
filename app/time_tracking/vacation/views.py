from datetime import date, timedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Sum
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from time_tracking.vacation.models import Vacation
from time_tracking.vacation.permissions import IsOwner
from time_tracking.vacation.serializers import VacationSerializer
from time_tracking.event.models import Event


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

        vacations_count = Vacation.objects.filter(
            owner=self.request.user,
            start_date__gte=date(timezone.now().year, 1, 1),
        ).aggregate(Sum('number_of_days'))['number_of_days__sum']

        if vacations_count is not None:
            if vacations_count >= 16:
                return Response(
                    {"detail": _("Reached max vacations days")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            remaining_days = 16 - vacations_count
            if remaining_days-serializer.validated_data['number_of_days'] < 0:
                return Response(
                    {"detail": _("Can't add more than %(days)s") % {
                        'days': remaining_days
                    }},
                    status=status.HTTP_400_BAD_REQUEST
                )

        last_vacation_date = (
                serializer.validated_data['start_date'] +
                timedelta(days=serializer.validated_data['number_of_days'])
        )

        events_intersection = Event.objects.filter(
            start_date__lte=last_vacation_date,
            end_date__gte=serializer.validated_data['start_date']
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
