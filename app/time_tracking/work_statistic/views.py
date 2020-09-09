from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, F, Min, Max, TimeField, DateField
from django.db.models.functions import TruncDay, TruncTime
from django.utils import timezone
from django.core.cache import cache

from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from time_tracking.work_statistic.serializers import (
    EmployeesArrivalAndLeavingTimesSerializer,
    TeamWorkingToLeavingTimeStatisticsSerializer,
    UserTotalWorkingHoursStatisicsSerializer,
    UsersAvailableWorkTimeStatisticsSerializer,
)
from time_tracking.work_time.models import WorkTime


class WorkTimeUsersAvailableStatistics(viewsets.ReadOnlyModelViewSet):
    """
    List the users and there available statistics
    """
    serializer_class = UsersAvailableWorkTimeStatisticsSerializer
    permission_classes = [IsAdminUser, ]

    def get_queryset(self):
        return User.objects.filter(is_staff=False)


class WorkTimeStatisticsDetail(APIView):
    """
    Retrieve work hours since a `week`, a `quarter` or a `year` ago.
    """
    permission_classes = [IsAdminUser, ]
    serializer_class = UserTotalWorkingHoursStatisicsSerializer
    # the periods names are only in lowercase
    period_name_with_days_count = {'week': 7, 'quarter': 91, 'year': 356}

    def get_queryset(self):
        return WorkTime.objects.filter(
            end_datetime__isnull=False,
            owner__is_staff=False,
        )

    def calculate_working_hours(self, queryset):
        calc = queryset.annotate(
            diff=F('end_datetime') - F('start_datetime')
        ).values('diff').aggregate(sum=Sum('diff'))
        seconds_sum = (calc['sum'] or timedelta()).total_seconds()
        return seconds_sum / 3600

    def get(self, request, period, user_id):
        period = period.lower()
        days_count = self.period_name_with_days_count.get(period)
        if days_count is None or User.objects.filter(pk=user_id).exists() is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        total_working_hours = cache.get(f'total_working_hours_for_a_{period}_to_user_{user_id}')

        if total_working_hours is None:
            today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            previous_datetime = today_datetime - timedelta(days=days_count)

            total_working_hours = self.calculate_working_hours(
                self.get_queryset().filter(
                    owner=user_id,
                    start_datetime__gte=previous_datetime
                ).exclude(start_datetime__gt=today_datetime)
            )
            cache.set(
                f'total_working_hours_for_a_{period}_to_user_{user_id}',
                total_working_hours,
                timedelta(hours=1).total_seconds()
            )

        serializer = self.serializer_class({
            'total_working_hours': total_working_hours
        })

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class EmployeesArrivalAndLeavingTimesStatisticsDetail(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Retrieve the employee arrival time and leaving time.
    """
    permission_classes = [IsAdminUser, ]
    serializer_class = EmployeesArrivalAndLeavingTimesSerializer
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        return User.objects.filter(is_staff=False)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        query = WorkTime.objects.filter(owner=user).values(
            day=TruncDay('start_datetime'),
        ).annotate(
            min=TruncTime(Min('start_datetime')),
            max=TruncTime(Max('end_datetime')),
        )

        employees_stats = cache.get_or_set(
            f'avg_arrival_and_leaving_time_for_user_{user.pk}',
            query.aggregate(
                avg_start=Avg('min', output_field=TimeField()),
                avg_end=Avg('max', output_field=TimeField())),
            timedelta(hours=1).total_seconds()
        )

        avg_arrival = None
        avg_leave = None

        if employees_stats['avg_start'] is not None:
            avg_arrival = datetime.utcfromtimestamp(employees_stats['avg_start'].total_seconds()).time()

        if employees_stats['avg_end'] is not None:
            avg_leave = datetime.utcfromtimestamp(employees_stats['avg_end'].total_seconds()).time()

        serializer = self.get_serializer({
            'username': user.username,
            'average_arrival_time': avg_arrival,
            'average_leaving_time': avg_leave,
        })
        return Response(serializer.data)


class WorkingHoursToLeavingHoursStatisticsDetail(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Retrieve the team working hours to leaving hours
    """
    permission_classes = [IsAdminUser, ]
    serializer_class = TeamWorkingToLeavingTimeStatisticsSerializer

    def list(self, request, *args, **kwargs):
        """
        working time = select all the time and sum it together
        leaving time = sum all the leaving time per day for the user and sum them
        """
        query = User.objects.filter(is_staff=False, work_times__end_datetime__isnull=False).annotate(
            work_time=F('work_times__end_datetime') - F('work_times__start_datetime'),
            end_datetime=F('work_times__end_datetime'),
            start_datetime=F('work_times__start_datetime'),
            day=TruncDay('work_times__start_datetime', output_field=DateField())
        ).values('username', 'day').annotate(
            total_work_time_per_day=Sum('work_time'),
            start_to_end_time_per_day=(Max('end_datetime') - Min('start_datetime'))
        ).values(
            'username', 'total_work_time_per_day', 'start_to_end_time_per_day'
        )

        stats = cache.get_or_set(
            'team_work_to_leave_hours', query.aggregate(
                leaving_hours=Sum(F('start_to_end_time_per_day') - F('total_work_time_per_day')),
                working_hours=Sum('total_work_time_per_day')),
            timedelta(days=1).total_seconds()
        )

        working_hours = (stats['working_hours'] or timedelta()).total_seconds() / 3600
        leaving_hours = (stats['leaving_hours'] or timedelta()).total_seconds() / 3600
        work_on_leve_time = None
        if leaving_hours != 0:
            work_on_leve_time = working_hours / leaving_hours * 100

        serializer = self.get_serializer({
            'working_hours': working_hours,
            'leaving_hours': leaving_hours,
            'percentage_of_working_on_leaving_time': work_on_leve_time,
        })

        return Response(serializer.data, status.HTTP_200_OK)
