from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime


PERIODS_NAMES = dict(week='week', quarter='quarter', year='year')


def detail_url(period, user_id):
    """Return work-time statistics detail URL"""
    return reverse('work-time-periods-statistic', args=[period, user_id])


class PublicWorkTimeStatisticsDetailApiTests(TestCase):
    """Test the publicly available statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user',
            'test@test.com',
            '123qwe',
            is_staff=False,
        )

    def test_accessing_the_endpoint_without_logged_in_user(self):
        """
        Test that login is required to access the users available statistics endpoint
        """
        url = detail_url(PERIODS_NAMES['week'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class NoneStaffMemberWorkTimeStatisticsDetailApiTests(TestCase):
    """Test the None Staff Members statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user',
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_accessing_the_endpoint_with_logged_in_user(self):
        """
        Test that access the users statistics endpoint is not allowed for the users
        """
        url = detail_url(PERIODS_NAMES['week'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StaffMemberWorkTimeStatisticsDetailApiTests(TestCase):
    """Test the Staff Members statistic API"""

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

    def test_accessing_the_week_statistics_endpoint_with_logged_in_staff_member(self):
        """
        Test that access the users' week statistics endpoint is available for staff members
        """
        url = detail_url(PERIODS_NAMES['week'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 0})

    def test_accessing_the_quarter_statistics_endpoint_with_logged_in_staff_member(self):
        """
        Test that access the users' quarter statistics endpoint is available for staff members
        """
        url = detail_url(PERIODS_NAMES['quarter'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 0})

    def test_accessing_the_year_statistics_endpoint_with_logged_in_staff_member(self):
        """
        Test that access the users' year statistics endpoint is available for staff members
        """
        url = detail_url(PERIODS_NAMES['year'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 0})

    def test_the_period_string_is_case_insensitive(self):
        """
        Test that the period string is case insensitive
        """
        url_lowercase = detail_url(PERIODS_NAMES['week'].lower(), self.user.pk)
        url_uppercase = detail_url(PERIODS_NAMES['week'].upper(), self.user.pk)
        res_lower = self.client.get(url_lowercase)
        res_upper = self.client.get(url_uppercase)

        self.assertEqual(res_lower.status_code, status.HTTP_200_OK)
        self.assertEqual(res_lower.data, {'total_working_hours': 0})

        self.assertEqual(res_upper.status_code, status.HTTP_200_OK)
        self.assertEqual(res_upper.data, {'total_working_hours': 0})

    def test_total_working_hours_for_the_week(self):
        """
        Test the total working hours result for this week
        """
        today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_week_start = today_datetime - timedelta(weeks=1)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=this_week_start - timedelta(days=1),
                end_datetime=this_week_start - timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime + timedelta(days=1),
                end_datetime=today_datetime + timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_week_start + timedelta(days=1),
                end_datetime=this_week_start + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_week_start,
                end_datetime=this_week_start + timedelta(hours=2, minutes=50, microseconds=50),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_week_start + timedelta(days=1),
                end_datetime=this_week_start + timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_week_start + timedelta(days=1, hours=9),
                end_datetime=this_week_start + timedelta(days=1, hours=11),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime,
                end_datetime=today_datetime + timedelta(hours=2, minutes=10),
                owner=self.user,
            ),
        ])
        url = detail_url(PERIODS_NAMES['week'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 9})

    def test_total_working_hours_for_the_quarter(self):
        """
        Test the total working hours result for this quarter
        """
        today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_quarter_start = today_datetime - timedelta(days=91)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=this_quarter_start - timedelta(days=1),
                end_datetime=this_quarter_start - timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime + timedelta(days=1),
                end_datetime=today_datetime + timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_quarter_start + timedelta(days=1),
                end_datetime=this_quarter_start + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_quarter_start,
                end_datetime=this_quarter_start + timedelta(hours=2, minutes=50, microseconds=50),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_quarter_start + timedelta(days=15),
                end_datetime=this_quarter_start + timedelta(days=15, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_quarter_start + timedelta(days=55, hours=9),
                end_datetime=this_quarter_start + timedelta(days=55, hours=11),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime,
                end_datetime=today_datetime + timedelta(hours=2, minutes=10),
                owner=self.user,
            ),
        ])
        url = detail_url(PERIODS_NAMES['quarter'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 9})

    def test_total_working_hours_for_the_year(self):
        """
        Test the total working hours result for this year
        """
        today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_year_start = today_datetime - timedelta(days=356)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=this_year_start - timedelta(days=1),
                end_datetime=this_year_start - timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime + timedelta(days=1),
                end_datetime=today_datetime + timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=1),
                end_datetime=this_year_start + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start,
                end_datetime=this_year_start + timedelta(hours=2, minutes=50, microseconds=50),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=121),
                end_datetime=this_year_start + timedelta(days=121, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=333, hours=9),
                end_datetime=this_year_start + timedelta(days=333, hours=11),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime,
                end_datetime=today_datetime + timedelta(hours=2, minutes=10),
                owner=self.user,
            ),
        ])
        url = detail_url(PERIODS_NAMES['year'], self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 9})

    def test_the_staff_members_statistics_should_return_zero(self):
        """
        Test the total working hours result for the staff members should be zero
        """
        this_week_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(weeks=1)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=this_week_start + timedelta(days=1),
                end_datetime=this_week_start + timedelta(days=1, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_week_start + timedelta(days=1),
                end_datetime=this_week_start + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_week_start + timedelta(days=1),
                end_datetime=this_week_start + timedelta(days=1, hours=2),
                owner=self.admin,
            ),
        ])
        url = detail_url(PERIODS_NAMES['year'], self.admin.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'total_working_hours': 0})

