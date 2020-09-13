from django.utils.translation import gettext as _
from rest_framework import serializers

from time_tracking.event.models import Event


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = [
            'id', 'url', 'title', 'description', 'start_date', 'end_date'
        ]

    def validate(self, data):
        """
        Check that start date is before end date
        """
        if data.get('start_date') is None:
            start_date = self.instance.start_date
        else:
            start_date = data['start_date']

        if data.get('end_date') is None:
            end_date = self.instance.end_date
        else:
            end_date = data['end_date']

        if start_date > end_date:
            raise serializers.ValidationError(
                _("End date must occur after Start date")
            )
        return data
