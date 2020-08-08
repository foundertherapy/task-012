from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.db.models import Count

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from time_tracking.work_time.models import WorkTime


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def week_statistics_detail(request, format=None):
    """
    Retrieve work time since a week ago.
    """
    if request.method == 'GET':
        work_times = WorkTime.objects.filter(
            owner=request.user,
            work_time__isnull=False,
            end_time__gt=timezone.now() - timedelta(weeks=1)
        ).aggregate(Sum('work_time'))
        responce = {
            "total_working_time_in_seconds": work_times['work_time__sum']
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
            work_time__isnull=False,
            end_time__gt=timezone.now() - timedelta(weeks=13)
        ).aggregate(Sum('work_time'))
        responce = {
            "total_working_time_in_seconds": work_times['work_time__sum']
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
            work_time__isnull=False,
            end_time__gt=timezone.now() - timedelta(days=356)
        ).aggregate(Sum('work_time'))
        responce = {
            "total_working_time_in_seconds": work_times['work_time__sum']
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
        for user in User.objects.filter(is_staff=False):
            avg_work_time_starts = WorkTime.objects.filter(
                owner=user
            ).aggregate(
                Avg('start_unix_time')
            )['start_unix_time__avg']

            avg_work_time_ends = WorkTime.objects.filter(
                owner=user
            ).aggregate(
                Avg('end_unix_time')
            )['end_unix_time__avg']

            if avg_work_time_starts is not None:
                avg_work_time_starts = datetime.fromtimestamp(
                    avg_work_time_starts
                )
            if avg_work_time_ends is not None:
                avg_work_time_ends = datetime.fromtimestamp(
                    avg_work_time_ends
                )

            responce.append({
                'user': user.username,
                'average_arrival_time': avg_work_time_starts,
                'average_leaving_time': avg_work_time_ends,
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
        working_hours = 0
        leaving_hours = 0
        for user in User.objects.filter():
            work_times = WorkTime.objects.filter(
                owner=user,
                end_unix_time__isnull=False,
                start_unix_time__isnull=False
            ).values(
                'days_count', 'start_unix_time', 'end_unix_time'
            ).annotate(days=Count('days_count')).order_by('-start_unix_time')

            length = len(work_times)
            index = 0

            for work_time in work_times:
                working_hours += work_time['end_unix_time']\
                                 - work_time['start_unix_time']
                if ++index < length - 1:
                    leaving_hours += work_times[index]['start_unix_time']\
                                     - work_time['end_unix_time']

        if working_hours == 0 or leaving_hours == 0:
            work_over_leave = 0
        else:
            work_over_leave = working_hours / leaving_hours
        response = {
            'working_time': working_hours,
            'leaving_time': leaving_hours,
            'work_on_leave_time': work_over_leave,
        }

        return Response(response, status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)
