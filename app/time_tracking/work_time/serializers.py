from django.utils.translation import gettext as _
from rest_framework import serializers
from time_tracking.work_time.models import WorkTime


class WorkTimeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = WorkTime
        fields = [
            'id', 'url', 'created_at', 'updated_at',
            'start_datetime', 'end_datetime', 'owner'
        ]

    def validate(self, data):
        """
        Check that start date is before end date
        """
        if data.get('end_datetime') is None and self.instance is not None:
            end_date = self.instance.end_datetime
        else:
            end_date = data.get('end_datetime')

        if end_date is None:
            return data

        if data.get('start_datetime') is None:
            start_date = self.instance.start_datetime
        else:
            start_date = data['start_datetime']

        if start_date > end_date:
            raise serializers.ValidationError(
                _("Checkout must occur after Checkin datetime")
            )
        return data
