from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime


CHECK_IN_URL = reverse('worktime-checkin-list')


class PublicCheckInsApiTests(TestCase):
    """Test the publicly available check-ins API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(CHECK_IN_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_checkin_without_authentication_should_fail(self):
        """Test that login is required to create a new check-in"""
        payload = {}
        res = self.client.post(CHECK_IN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCheckInsApiTests(TestCase):
    """Test the private check-ins API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_create_checkin_successful(self):
        """Test create a new check-in"""
        payload = {}
        res = self.client.post(CHECK_IN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = WorkTime.objects.filter(
            unix_start_time__isnull=False,
            unix_end_time__isnull=True,
            owner=self.user,
        ).exists()
        self.assertTrue(exists)

    def test_create_checkin_while_checked(self):
        """
        Test create a new check-in while the old check-in doesn't have checkout
        """
        work_time = WorkTime(owner=self.user)
        work_time.save()
        payload = {}
        res = self.client.post(CHECK_IN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
