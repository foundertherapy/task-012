from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_statistic.serializers import UsersAvailableWorkTimeStatisticsSerializer

AVAILABLE_STATISTICS_URL = reverse(
    'worktime-available-statistics-list'
)


def detail_url(user_id):
    """Return work-time available statistics detail URL"""
    return reverse('worktime-available-statistics-detail', args=[user_id])


class PublicWorkTimeUsersAvailableStatisticsApiTests(TestCase):
    """Test the publicly available statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )

    def test_accessing_the_endpoint_without_logged_in_user(self):
        """
        Test that login is required to access the users available statistics endpoint
        """
        res = self.client.get(AVAILABLE_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accessing_the_detail_endpoint_without_logged_in_user(self):
        """
        Test that login is required to access the detail users available statistics endpoint
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class NoneStaffMemberWorkTimeUsersAvailableStatisticsApiTests(TestCase):
    """Test the None Staff Members Statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_accessing_the_endpoint_with_logged_in_user(self):
        """
        Test that the users available statistics endpoint is not allowed for the users
        """
        res = self.client.get(AVAILABLE_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_accessing_the_detail_endpoint_with_logged_in_user(self):
        """
        Test that the detail users available statistics endpoint is not allowed for the users
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StaffMembersWorkTimeUsersAvailableStatisticsApiTests(TestCase):
    """Test the Staff Members Statistic API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
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
        get_user_model().objects.create_user(
            'other-test-user'
            'other-test@test.com',
            '123qwe',
            is_staff=False,
        )

        self.client.force_authenticate(self.admin)

    def test_list_users_should_be_allowed_for_staff_members(self):
        """
        Test that the users available statistics list is available for staff members
        """
        res = self.client.get(AVAILABLE_STATISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_user_should_be_allowed_for_staff_members(self):
        """
        Test that the user available statistics detail is available staff members
        """
        url = detail_url(self.user.pk)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

