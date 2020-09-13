from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel


class Event(TimeStampedModel):

    created_by = models.ForeignKey(
        User, limit_choices_to={'is_staff': True},
        on_delete=models.SET_NULL,
        related_name='+', null=True
    )

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['-start_date']
