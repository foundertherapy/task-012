from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers

from time_tracking.vacation.models import Vacation


class VacationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Vacation
        fields = [
            'id', 'url', 'brief_description',
            'start_date', 'end_date', 'owner'
        ]

    def validate(self, data):
        """
        Check that start date is not after the end date
        """
        if data.get('end_date') is None:
            end_date = self.instance.end_date
        else:
            end_date = data['end_date']

        if data.get('start_date') is None:
            start_date = self.instance.end_date
        else:
            start_date = data['start_date']

        if end_date < start_date:
            raise serializers.ValidationError(
                _("end_date must not occur before start_date")
            )

        if (end_date - start_date).days + 1 > 16:
            raise serializers.ValidationError(
                _("You can't have a vacation for more than 16 day!")
            )
        return data

    def validate_start_date(self, value):
        """
        Check that the start_date was not modify and that
        the start_date is not on the past
        """
        if self.instance and self.instance.start_date != value:
            raise serializers.ValidationError(
                _("Changing start_date is not allowed")
            )

        if self.instance is None and value < timezone.now().date():
            raise serializers.ValidationError(
                _("start_date can not be from the past")
            )
        return value

    def validate_end_date(self, value):
        """
        Check that the end_date was not modify
        """
        if self.instance and self.instance.end_date != value:
            raise serializers.ValidationError(
                _("Changing end_date is not allowed")
            )

        if self.instance is None and value < timezone.now().date():
            raise serializers.ValidationError(
                _("end_date can not be from the past")
            )
        return value
