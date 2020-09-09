from rest_framework import serializers
from django.contrib.auth.models import User
from django.urls import reverse


class EmployeesArrivalAndLeavingTimesSerializer(serializers.Serializer):
    username = serializers.StringRelatedField()
    average_arrival_time = serializers.TimeField(allow_null=True)
    average_leaving_time = serializers.TimeField(allow_null=True)


class TeamWorkingToLeavingTimeStatisticsSerializer(serializers.Serializer):
    working_hours = serializers.IntegerField()
    leaving_hours = serializers.IntegerField()
    percentage_of_working_on_leaving_time = serializers.FloatField()


class UserTotalWorkingHoursStatisicsSerializer(serializers.Serializer):
    total_working_hours = serializers.IntegerField()


class UsersAvailableWorkTimeStatisticsSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

    working_hours_to_leaving_hours = serializers.HyperlinkedIdentityField(
        view_name='work-arrival-and-leaving-time-statistic-detail',
        lookup_url_kwarg='user_id',
    )
    total_working_hours = serializers.SerializerMethodField()

    url = serializers.HyperlinkedIdentityField(view_name='worktime-available-statistics-detail')

    class Meta:
        model = User
        fields = [
            'id', 'url', 'username', 'total_working_hours', 'working_hours_to_leaving_hours'
        ]

    def get_total_working_hours(self, obj):
        return {
            'year': reverse(
                'work-time-periods-statistic',
                kwargs={
                    'period': 'year',
                    'user_id': obj.pk
                }
            ),
            'quarter': reverse(
                'work-time-periods-statistic',
                kwargs={
                    'period': 'quarter',
                    'user_id': obj.pk
                }
            ),
            'week': reverse(
                'work-time-periods-statistic',
                kwargs={
                    'period': 'week',
                    'user_id': obj.pk
                }
            ),
        }
