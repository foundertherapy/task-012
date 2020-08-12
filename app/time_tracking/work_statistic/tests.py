from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime, convert_time_to_unix
from time_tracking.work_time.serializers import convert_unix_to_time


WEEK_STATISTIC_URL = reverse('worktime-week-statistic')
QUARTER_STATISTIC_URL = reverse('worktime-quarter-statistic')
YEAR_STATISTIC_URL = reverse('worktime-year-statistic')

ARRIVAL_AND_LEAVING_STATISTIC_URL = reverse(
    'work-arrival-and-leaving-time-statistic'
)
WORK_TO_LEAVE_STATISTIC_URL = reverse(
    'work-hours-to-leave-hours-statistic'
)


def sample_work_time(user, start_days_ago=1,
                     work_hours=8.0, **params):
    """Create and return a sample WorkTime"""
    # start_days_ago should be more than 1 to prevent the work_time
    # form starting on a day and ending on a different day based on the
    # time we run the test on
    if start_days_ago < 1:
        raise ValueError('''
        'start_days_ago' can't be less then 1
        ''')

    start_time = timezone.now() - timedelta(days=start_days_ago)
    unix_start = convert_time_to_unix(start_time)
    unix_end = unix_start + timedelta(hours=work_hours).total_seconds()
    defaults = {
        'start_date': start_time.date(),
        'unix_start_time': unix_start,
        'unix_end_time': unix_end,
    }

    defaults.update(params)
    wt = WorkTime.objects.create(owner=user, **defaults)
    wt.save()
    wt.unix_start_time = defaults['unix_start_time']
    wt.start_date = defaults['start_date']
    wt.save()
    return wt


class PrivateStatisticApiTests(TestCase):
    """Test the private Statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

        # Last week 63,5 H
        sample_work_time(self.user, start_days_ago=1, work_hours=7)
        sample_work_time(self.user, start_days_ago=2, work_hours=8)
        sample_work_time(self.user, start_days_ago=3, work_hours=9)
        sample_work_time(self.user, start_days_ago=4, work_hours=4)
        sample_work_time(self.user, start_days_ago=5, work_hours=6)
        sample_work_time(self.user, start_days_ago=6, work_hours=3.5)
        wt = sample_work_time(self.user, start_days_ago=7, work_hours=26)
        self.work_time_w = WorkTime.objects.filter(id__lte=wt.id)
        self.this_week_working_hours = 63.5

        # 10 weeks ago 15,5 H
        sample_work_time(self.user, start_days_ago=70, work_hours=7.5)
        wt = sample_work_time(self.user, start_days_ago=68, work_hours=8)
        self.work_time_q = WorkTime.objects.filter(id__lte=wt.id)
        self.this_quarter_working_hours = self.this_week_working_hours + 15.5

        # 23 week ago 13 H
        sample_work_time(self.user, start_days_ago=162, work_hours=5)
        wt = sample_work_time(self.user, start_days_ago=350, work_hours=8)
        self.work_time_y = WorkTime.objects.filter(id__lte=wt.id)
        self.this_year_working_hours = self.this_quarter_working_hours + 13

    def test_should_retrieve_this_week_working_time_successfully(self):
        """Test get this week working time"""
        res = self.client.get(WEEK_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['total_working_time_in_seconds'],
            int(
                self.this_week_working_hours * 60 * 60
            )
        )

    def test_should_retrieve_this_quarter_working_time_successfully(self):
        """Test get this quarter working time"""
        res = self.client.get(QUARTER_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['total_working_time_in_seconds'],
            int(
                self.this_quarter_working_hours * 60 * 60
            )
        )

    def test_should_retrieve_this_year_working_time_successfully(self):
        """Test get this year working time"""
        res = self.client.get(YEAR_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['total_working_time_in_seconds'],
            int(
                self.this_year_working_hours * 60 * 60
            )
        )

    def test_retrieve_average_arrival_and_leaving_time_of_the_employees(self):
        """
        Test get the arrival and leaving time for each employee
        """
        start_time = self.work_time_y.aggregate(avg=Avg('unix_start_time'))
        end_time = self.work_time_y.aggregate(avg=Avg('unix_end_time'))

        res = self.client.get(ARRIVAL_AND_LEAVING_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        stats = res.data[0]
        self.assertEqual(stats['user'], self.user.username)
        self.assertEqual(
            stats['average_arrival_time'],
            convert_unix_to_time(start_time['avg'])
        )
        self.assertEqual(
            stats['average_leaving_time'],
            convert_unix_to_time(end_time['avg'])
        )
