from rest_framework import serializers

from time_tracking.event.models import Event


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = [
            'id', 'url', 'title', 'description', 'start_date', 'end_date'
        ]
