from django.utils.translation import gettext as _
from django.utils import timezone
from rest_framework import serializers

from time_tracking.vacation.models import Vacation


class VacationSerializer(serializers.ModelSerializer):
    number_of_days = serializers.IntegerField(max_value=16, min_value=1)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Vacation
        fields = [
            'id', 'url', 'brief_description', 'start_date',
            'number_of_days', 'owner'
        ]

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

    def validate_number_of_days(self, value):
        """
        Check that the number_of_days was not modify
        """
        if self.instance and self.instance.number_of_days != value:
            raise serializers.ValidationError(
                _("Changing number_of_days is not allowed")
            )
        return value
