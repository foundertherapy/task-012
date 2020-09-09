from django.db import models
from django.contrib.auth.models import User


class Vacation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    brief_description = models.CharField(max_length=120, blank=True, default='')
    start_date = models.DateField()
    number_of_days = models.PositiveSmallIntegerField()
    owner = models.ForeignKey(
        User,
        limit_choices_to={'is_staff': False},
        on_delete=models.CASCADE,
        related_name='vacations_applications',
    )

    class Meta:
        ordering = ['-start_date']
