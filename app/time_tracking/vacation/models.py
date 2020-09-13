from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel


class Vacation(TimeStampedModel):

    brief_description = models.CharField(max_length=120, blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(
        User,
        limit_choices_to={'is_staff': False},
        on_delete=models.CASCADE,
        related_name='vacations_applications',
    )

    class Meta:
        ordering = ['-start_date']
