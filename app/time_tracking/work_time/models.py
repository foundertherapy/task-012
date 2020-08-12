from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


def convert_time_to_unix(date_time):
    """Convert the datetime.time/datetime.datetime to unix time"""
    return datetime.timedelta(
        hours=date_time.hour,
        minutes=date_time.minute,
        seconds=date_time.second,
    ).total_seconds()


class WorkTime(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    start_date = models.DateField(auto_now_add=True, editable=True)
    # this represents datetime.time
    unix_start_time = models.PositiveIntegerField()
    # this represents datetime.time
    unix_end_time = models.PositiveIntegerField(blank=True, null=True)

    owner = models.ForeignKey(
        User,
        limit_choices_to={'is_staff': False},
        on_delete=models.CASCADE,
        related_name='work_times',
    )

    def save(self, *args, **kwargs):
        """ On create, set start_time """
        if not self.pk:
            time_now = timezone.now()
            self.unix_start_time = convert_time_to_unix(time_now)

        return super(WorkTime, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date', '-unix_start_time']
