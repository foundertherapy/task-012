from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timesince import timesince
import time

class WorkTime(models.Model):
    start_time = models.DateTimeField(blank=False, null=False)
    end_time   = models.DateTimeField(blank=True, null=True)

    work_time  = models.PositiveIntegerField(blank=True, null=True, editable=False)

    start_unix_time = models.PositiveIntegerField(blank=False, null=False, editable=False)
    end_unix_time = models.PositiveIntegerField(blank=True, null=True, editable=False)

    days_count = models.PositiveIntegerField(blank=False, null=False, editable=False)

    owner = models.ForeignKey(
        User,
        limit_choices_to={'is_staff': False},
        on_delete=models.CASCADE,
        related_name='work_times',
    )

    def save(self, *args, **kwargs):
        """ On create, set start_time """
        if not self.id:
            time_now = timezone.now()
            self.start_time = time_now
            self.start_unix_time = time.mktime(time_now.timetuple())
            self.days_count = self.start_unix_time / 86400
        else:
            self.work_time = int((self.end_time - self.start_time).total_seconds())
            self.end_unix_time = time.mktime(self.end_time.timetuple())

        return super(WorkTime, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-start_time']
