from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime


WORK_TO_LEAVE_HOURS_STATISTICS_URL = reverse(
    'work-hours-to-leave-hours-statistic-list'
)


class PublicWorkingHoursToLeavingHoursStatisticsDetailApiTests(TestCase):
    """Test the publicly available workingHoursToLeavingHoursStatisticsDetailAPI"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )

    def test_accessing_the_statistics_endpoint_without_logged_in_user(self):
        """
        Test that login is required to access the statistics endpoint
        """
        res = self.client.get(WORK_TO_LEAVE_HOURS_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class NoneStaffMemberWorkingHoursToLeavingHoursStatisticsDetailApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_accessing_the_statistics_endpoint_with_logged_in_user(self):
        """
        Test that the statistics endpoint is not allowed to be accessed by the users
        """
        res = self.client.get(WORK_TO_LEAVE_HOURS_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StaffMembersWorkingHoursToLeavingHoursStatisticsDetailApiTests(TestCase):
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

    def test_accessing_the_statistic_endpoint_should_be_allowed_for_staff_members(self):
        """
        Test that the available statistics is available for staff members to view
        """
        res = self.client.get(WORK_TO_LEAVE_HOURS_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'working_hours': 0,
            'leaving_hours': 0,
            'percentage_of_working_on_leaving_time': None,
        })

    def test_the_accuracy_of_the_endpoint_results(self):
        """
        Test the accuracy of the end workingHoursToLeavingHoursStatisticsDetailAPI
        """
        today_datetime = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_year_start = today_datetime - timedelta(days=730)
        wts = WorkTime.objects.bulk_create([
            WorkTime(
                start_datetime=this_year_start - timedelta(days=1),
                end_datetime=this_year_start - timedelta(days=1, hours=2),
                owner=self.admin,
            ),
            WorkTime(
                start_datetime=today_datetime + timedelta(days=1),
                end_datetime=today_datetime + timedelta(days=1, hours=2),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=3, hours=8, minutes=30),
                end_datetime=this_year_start + timedelta(days=3, hours=19, minutes=30),
                owner=self.other_user,
            ),
            WorkTime(
                start_datetime=this_year_start,
                end_datetime=this_year_start + timedelta(hours=8, minutes=50, seconds=50),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=333),
                end_datetime=this_year_start + timedelta(days=333, hours=2),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=this_year_start + timedelta(days=333, hours=9),
                end_datetime=this_year_start + timedelta(days=333, hours=11),
                owner=self.user,
            ),
            WorkTime(
                start_datetime=today_datetime,
                end_datetime=today_datetime + timedelta(hours=2, minutes=50),
                owner=self.user,
            ),
        ])
        res = self.client.get(WORK_TO_LEAVE_HOURS_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['working_hours'], 28)
        self.assertEqual(res.data['leaving_hours'], 7)
        self.assertGreater(res.data['percentage_of_working_on_leaving_time'], 409.72222)
        self.assertLess(res.data['percentage_of_working_on_leaving_time'], 409.72223)
