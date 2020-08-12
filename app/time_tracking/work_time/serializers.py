import time
from datetime import datetime
from django.conf import settings
from django.utils.timezone import utc, localtime

from rest_framework import serializers
from time_tracking.work_time.models import WorkTime


def convert_unix_to_datetime(start_date, unix_time):
    """Convert the unix time to datetime.datetime"""
    if unix_time is None or start_date is None:
        return None
    unix_datetime = time.mktime(start_date.timetuple()) + unix_time
    if settings.USE_TZ:
        return localtime(
            datetime.utcfromtimestamp(unix_datetime).replace(tzinfo=utc)
        )
    else:
        return datetime.fromtimestamp(unix_datetime)


def convert_unix_to_time(unix_time):
    """Convert the unix time to datetime.time"""
    if unix_time is None:
        return None
    elif settings.USE_TZ:
        return localtime(
            datetime.utcfromtimestamp(unix_time).replace(tzinfo=utc)
        ).time()
    else:
        return datetime.fromtimestamp(unix_time).time()


class WorkTimeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkTime
        fields = ['id', 'url', 'created_at', 'updated_at',
                  'start_datetime', 'end_datetime']

    def get_start_datetime(self, obj):
        return convert_unix_to_datetime(obj.start_date, obj.unix_start_time)

    def get_end_datetime(self, obj):
        return convert_unix_to_datetime(obj.start_date, obj.unix_end_time)


class WorkTimeCheckInSerializer(serializers.ModelSerializer):
    start_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkTime
        fields = ['id', 'url', 'start_datetime']

    def get_start_datetime(self, obj):
        return convert_unix_to_datetime(obj.start_date, obj.unix_start_time)


class WorkTimeCheckOutSerializer(serializers.ModelSerializer):
    end_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkTime
        fields = ['id', 'url', 'end_datetime']

    def get_end_datetime(self, obj):
        return convert_unix_to_datetime(obj.start_date, obj.unix_end_time)
