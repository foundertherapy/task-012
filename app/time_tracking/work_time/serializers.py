from rest_framework import serializers

from time_tracking.work_time.models import WorkTime


class WorkTimeSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(read_only=True)
    end_time   = serializers.DateTimeField(read_only=True)
    work_time  = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkTime
        fields = ['id', 'url', 'start_time', 'work_time', 'end_time']



class WorkTimeCheckInSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = WorkTime
        fields = ['id', 'url', 'start_time']



class WorkTimeCheckOutSerializer(serializers.ModelSerializer):
    end_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = WorkTime
        fields = ['id', 'url', 'end_time']
