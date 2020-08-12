from django.db.models import Sum, Avg, F, Min, Max
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import FloatField

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from time_tracking.work_time.models import WorkTime
from time_tracking.work_time.serializers import convert_unix_to_time


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def week_statistics_detail(request, format=None):
    """
    Retrieve work time since a week ago.
    """
    if request.method == 'GET':
        work_times = WorkTime.objects.filter(
            owner=request.user,
            unix_end_time__isnull=False,
            start_date__gte=(
                    timezone.now() - timedelta(weeks=1)).date()
        ).annotate(
            diff=F('unix_end_time') - F('unix_start_time')
        ).values('diff').aggregate(Sum('diff'))

        responce = {
            "total_working_time_in_seconds": work_times['diff__sum']
        }

        return Response(responce, status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def quarter_statistics_detail(request, format=None):
    """
    Retrieve work time since a 13 weeks ago.
    """
    if request.method == 'GET':
        work_times = WorkTime.objects.filter(
            owner=request.user,
            unix_end_time__isnull=False,
            start_date__gte=(
                    timezone.now() - timedelta(weeks=13)).date()
        ).annotate(
            diff=F('unix_end_time') - F('unix_start_time')
        ).aggregate(Sum('diff'))
        responce = {
            "total_working_time_in_seconds": work_times['diff__sum']
        }

        return Response(responce, status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def year_statistics_detail(request, format=None):
    """
    Retrieve work time since a 356 days ago.
    """
    if request.method == 'GET':
        work_times = WorkTime.objects.filter(
            owner=request.user,
            unix_end_time__isnull=False,
            start_date__gte=(
                    timezone.now() - timedelta(days=356)).date()
        ).annotate(
            diff=F('unix_end_time') - F('unix_start_time')
        ).aggregate(Sum('diff'))
        responce = {
            "total_working_time_in_seconds": work_times['diff__sum']
        }

        return Response(responce, status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def employees_arrival_to_leaving_time_detail(request, format=None):
    """
    Retrieve the employees arrival time and leaving times.
    """
    if request.method == 'GET':
        responce = []

        employees_stats = User.objects.values(
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
            responce.append({
                'user': user,
                'average_arrival_time':
                    convert_unix_to_time(average_time['avg_start']),
                'average_leaving_time':
                    convert_unix_to_time(average_time['avg_end']),
            })

        return Response(responce, status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def working_ours_to_leaving_hours_detail(request, format=None):
    """
    Retrieve the team working hours to leaving hours
    """
    if request.method == 'GET':

        stats = User.objects.filter(
            work_times__unix_end_time__isnull=False
        ).annotate(
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
            worktime_sum_hours=Sum(
                'work_time', output_field=FloatField()
            ) / 3600.0,
        ).values(
            'start_to_end_hours', 'worktime_sum_hours'
        ).aggregate(
            leave_hours=Sum(F('start_to_end_hours') - F('worktime_sum_hours')),
            work_hours=Sum('worktime_sum_hours'),
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

    return Response(status=status.HTTP_400_BAD_REQUEST)
