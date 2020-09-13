from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime


def detail_url(user_id):
    """Return event detail URL"""
    return reverse('work-arrival-and-leaving-time-statistic-detail', args=[user_id])


class PublicEmployeesArrivalAndLeavingTimesStatisticsDetailApiTests(TestCase):
    """Test the publicly available employeesArrivalAndLeavingTimesStatisticsDetail API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )

    def test_accessing_the_detail_endpoint_without_logged_in_user(self):
        """
        Test that login is required to access the detail users statistic endpoint
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class NoneStaffMemberEmployeesArrivalAndLeavingTimesStatisticsDetailApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_accessing_the_detail_endpoint_with_logged_in_user(self):
        """
        Test that the detail users statistic endpoint is not allowed for the users
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StaffMembersEmployeesArrivalAndLeavingTimesStatisticsDetailApiTests(TestCase):
    """Test the Staff Members Statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.other_user = get_user_model().objects.create_user(
            'other-test-user',
            'other-test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.user = get_user_model().objects.create_user(
            'test-user',
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.admin = get_user_model().objects.create_user(
            'admin-test-user'
            'admin-test@test.com',
            '123qwe',
            is_staff=True,
        )
        self.client.force_authenticate(self.admin)

    def test_detail_user_should_be_allowed_for_staff_members(self):
        """
        Test that the user available statistics detail is available staff members
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], self.user.username)

    def test_that_none_will_be_return_when_there_are_no_records_for_the_user(self):
        """
        Test that the endpoint will return None when there are no records for the user
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'username': self.user.username,
            'average_arrival_time': None,
            'average_leaving_time': None,
        })

    def test_the_average_arrival_time_for_the_user(self):
        """
        Test that the return average_arrival_time for the user is correct
        """
        today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_year_start = today_datetime - timedelta(days=712)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=today_datetime + timedelta(days=1),
                end_datetime=today_datetime + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=101, minutes=23),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start,
                end_datetime=this_year_start + timedelta(days=1, hours=2, seconds=31),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=121, hours=11),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=333, hours=3),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=1, hours=1, minutes=50, seconds=5, milliseconds=500, microseconds=500),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime,
                owner=self.user,
            ),
        ])
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], self.user.username)
        self.assertEqual(res.data['average_arrival_time'], '03:10:01.100100')

    def test_the_average_leaving_time_for_the_user(self):
        """
        Test that the return average_leaving_time for the user is correct
        """
        today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_year_start = today_datetime - timedelta(days=712)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=today_datetime + timedelta(days=1),
                end_datetime=today_datetime + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=101, minutes=23),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start,
                end_datetime=this_year_start + timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=121, hours=11),
                end_datetime=this_year_start + timedelta(days=1, hours=23, minutes=48, seconds=9),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=333, hours=3),
                end_datetime=this_year_start + timedelta(days=1, hours=10, seconds=51, microseconds=320),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=1, hours=1, minutes=49, seconds=5, microseconds=500500),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime,
                end_datetime=this_year_start + timedelta(days=1, hours=7, seconds=34, milliseconds=404),
                owner=self.user,
            ),
        ])
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], self.user.username)
        self.assertEqual(res.data['average_leaving_time'], '10:42:23.601080')
