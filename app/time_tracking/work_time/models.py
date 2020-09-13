from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel


class WorkTime(TimeStampedModel):

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey(
        User,
        limit_choices_to={'is_staff': False},
        on_delete=models.CASCADE,
        related_name='work_times',
    )

    class Meta:
        ordering = ['-start_datetime']
