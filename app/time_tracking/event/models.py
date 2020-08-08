from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(auto_now_add=False)
    end_date = models.DateField(auto_now_add=False)

    class Meta:
        ordering = ['-start_date']
