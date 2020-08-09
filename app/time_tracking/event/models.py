from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(auto_now_add=False)
    end_date = models.DateField(auto_now_add=False)
    created_by = models.ForeignKey(User, limit_choices_to={'is_staff': True},
                                   on_delete=models.SET_NULL,
                                   related_name='+', null=True)

    class Meta:
        ordering = ['-start_date']
