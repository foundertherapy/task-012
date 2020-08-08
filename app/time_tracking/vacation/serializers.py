from rest_framework import serializers

from time_tracking.vacation.models import Vacation


class VacationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='vacation-detail')
    brief_description = serializers.CharField(
        required=False, allow_blank=True, max_length=120
    )
    start_date = serializers.DateField()
    number_of_days = serializers.IntegerField(max_value=16, min_value=1)
    owner = serializers.ReadOnlyField(source='owner.username')

    def create(self, validated_data):
        """
        Create and return a new `Vacation` instance,
        given the validated data.
        """
        return Vacation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Vacation` instance,
        given the validated data.
        """
        instance.brief_description = validated_data.get(
            'brief_description', instance.brief_description
        )
        instance.start_date = validated_data.get(
            'start_date', instance.start_date
        )
        instance.number_of_days = validated_data.get(
            'number_of_days', instance.number_of_days
        )
        instance.save()
        return instance
