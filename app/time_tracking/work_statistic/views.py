from django.db.models import Sum, Avg, F, Min, Max
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import FloatField

from rest_framework.permissions import IsAuthenticated
from time_tracking.work_time.models import WorkTime
from time_tracking.work_time.serializers import convert_unix_to_time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class WorkTimeStatisticsDetail(APIView):
    """
    Retrieve work time since a `week`, a `quarter` or a `year` ago.
    """
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return WorkTime.objects.filter(
            owner=self.request.user,
            unix_end_time__isnull=False,
        )

    def calculate_work_times(self, queryset):
        return queryset.annotate(
            diff=F('unix_end_time') - F('unix_start_time')
        ).values('diff').aggregate(sum=Sum('diff'))

    def get_statistics_before(self, **kwargs):
        """
        Calculates the work time since a previous date.
        """
        previous_date = (
                timezone.now() - timedelta(**kwargs)
        ).date()

        work_times = self.calculate_work_times(
            self.get_queryset().filter(
                start_date__gte=previous_date
            )
        )

        return Response(
            {"total_working_time_in_seconds": work_times['sum']},
            status.HTTP_200_OK
        )

    def get(self, request, period, form=None):

        if period.lower() == 'week':
            return self.get_statistics_before(weeks=1)
        elif period == 'quarter':
            return self.get_statistics_before(weeks=13)
            pass
        elif period == 'year':
            return self.get_statistics_before(days=356)
            pass

        return Response(status=status.HTTP_400_BAD_REQUEST)


class EmployeesArrivalAndLeavingTimesStatisticsDetail(APIView):
    """
    Retrieve the employees arrival time and leaving times.
    """
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return User.objects.all()

    def get(self, request, form=None):
        response = []

        employees_stats = self.get_queryset().values(
            'work_times__start_date', 'username'
        ).annotate(
            min=Min('work_times__unix_start_time'),
            max=Max('work_times__unix_end_time')
        ).values(
            'username', 'min', 'max'
        )

        users = User.objects.all().values_list('username', flat=True)
        for user in users:
            average_time = employees_stats.filter(
                username=user
            ).values('min', 'max').aggregate(
                avg_start=Avg('min'),
                avg_end=Avg('max')
            )
            response.append({
                'user': user,
                'average_arrival_time':
                    convert_unix_to_time(average_time['avg_start']),
                'average_leaving_time':
                    convert_unix_to_time(average_time['avg_end']),
            })

        return Response(response, status.HTTP_200_OK)


class WorkingHoursToLeavingHoursStatisticsDetail(APIView):
    """
    Retrieve the team working hours to leaving hours
    """
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return User.objects.filter(
            work_times__unix_end_time__isnull=False
        )

    def get(self, request, form=None):
        stats = self.get_queryset().annotate(
            work_time=F(
                'work_times__unix_end_time'
            ) - F(
                'work_times__unix_start_time'
            )
        ).values(
            'work_times__start_date', 'username'
        ).annotate(
            start_to_end_hours=(Max(
                'work_times__unix_end_time', output_field=FloatField()
            ) - Min(
                'work_times__unix_start_time', output_field=FloatField()
            )) / 3600.0,
            work_time_sum_hours=Sum(
                'work_time', output_field=FloatField()
            ) / 3600.0,
        ).values(
            'start_to_end_hours', 'work_time_sum_hours'
        ).aggregate(
            leave_hours=Sum(
                F('start_to_end_hours') - F('work_time_sum_hours')
            ),
            work_hours=Sum('work_time_sum_hours'),
        )

        if stats['leave_hours'] == 0:
            work_over_leave = None
        else:
            work_over_leave = stats['work_hours'] / stats['leave_hours'] * 100

        response = {
            'working_hours': stats['work_hours'],
            'leaving_hours': stats['leave_hours'],
            'work_on_leave_hours': work_over_leave,
        }

        return Response(response, status.HTTP_200_OK)
