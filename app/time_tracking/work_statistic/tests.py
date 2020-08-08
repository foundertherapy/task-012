from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.urls import reverse
from django.test import TestCase
from datetime import timedelta, datetime

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime


WEEK_STATISTIC_URL = reverse('worktime-week-statistic')
QUARTER_STATISTIC_URL = reverse('worktime-quarter-statistic')
YEAR_STATISTIC_URL = reverse('worktime-year-statistic')

ARRIVAL_AND_LEAVING_STATISTIC_URL = reverse(
    'work-arrival-and-leaving-time-statistic'
)


class PrivateStatisticApiTests(TestCase):
    """Test the private Statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '123qwe'
        )
        self.client.force_authenticate(self.user)

        self.this_week = timedelta(hours=1.5)
        work_time = WorkTime(owner=self.user)
        work_time.save()
        work_time.end_time = work_time.start_time + self.this_week
        work_time.save()

        self.this_quarter = timedelta(days=7.55)
        work_time = WorkTime(owner=self.user)
        work_time.save()
        work_time.start_time = work_time.start_time - timedelta(weeks=10)
        work_time.end_time = work_time.start_time + self.this_quarter
        work_time.save()

        self.this_year = timedelta(weeks=23.5)
        work_time = WorkTime(owner=self.user)
        work_time.save()
        work_time.start_time = work_time.start_time - timedelta(days=364)
        work_time.end_time = work_time.start_time + self.this_year
        work_time.save()

    def test_should_retrieve_this_week_working_time_successfully(self):
        """Test get this week working time"""
        res = self.client.get(WEEK_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['total_working_time_in_seconds'],
            int(self.this_week.total_seconds())
        )

    def test_should_retrieve_this_quarter_working_time_successfully(self):
        """Test get this quarter working time"""
        res = self.client.get(QUARTER_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['total_working_time_in_seconds'],
            int(
                self.this_quarter.total_seconds()
                + self.this_week.total_seconds()
            )
        )

    def test_should_retrieve_this_year_working_time_successfully(self):
        """Test get this year working time"""
        res = self.client.get(YEAR_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['total_working_time_in_seconds'],
            int(
                self.this_year.total_seconds()
                + self.this_quarter.total_seconds()
                + self.this_week.total_seconds()
            )
        )

    def test_retrieve_average_arrival_and_leaving_time_of_the_employees(self):
        """
        Test get the arrival and leaving time for each employee
        """
        work_time_starts = WorkTime.objects.all().aggregate(
            Avg('start_unix_time')
        )['start_unix_time__avg']
        work_time_ends = WorkTime.objects.all().aggregate(
            Avg('end_unix_time')
        )['end_unix_time__avg']
        average_arrival_time = datetime.fromtimestamp(work_time_starts)
        average_leaving_time = datetime.fromtimestamp(work_time_ends)

        res = self.client.get(ARRIVAL_AND_LEAVING_STATISTIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            [{
                'user': self.user.username,
                'average_arrival_time': average_arrival_time,
                'average_leaving_time': average_leaving_time
            }])
