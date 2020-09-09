from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
