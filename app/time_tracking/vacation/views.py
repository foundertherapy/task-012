from rest_framework import permissions, viewsets
from django.utils import timezone
from django.db.models import Sum
from datetime import date

from rest_framework.response import Response
from rest_framework import mixins, generics, status

from time_tracking.vacation.models import Vacation
from time_tracking.vacation.permissions import IsOwner
from time_tracking.vacation.serializers import VacationSerializer

class VacationViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.ViewSetMixin,
                      generics.GenericAPIView):
    """
    This viewset provides `create`, `list` and `detail`
    actions for all the loged in users
    """
    serializer_class = VacationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Vacation.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):

        vacation_days_this_year = Vacation.objects.filter(
            owner=self.request.user,
            start_date__gt=date(timezone.now().year, 1, 1),
        ).aggregate(Sum('number_of_days'))['number_of_days__sum']

        if vacation_days_this_year is None:
            return super().create(request, *args, **kwargs)


        if vacation_days_this_year >= 16:
            return Response({"detail": "Sorry, you already reached the max vacations days a year."},status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if vacation_days_this_year+serializer.validated_data['number_of_days'] > 16:
                return Response({"detail": "Sorry, you can't add more than ["+ str(16-vacation_days_this_year) +"] day"},status=status.HTTP_406_NOT_ACCEPTABLE)
            return super().create(request, *args, **kwargs)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
