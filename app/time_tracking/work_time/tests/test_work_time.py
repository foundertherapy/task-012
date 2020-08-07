from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime
from time_tracking.work_time.serializers import WorkTimeSerializer


WORKTIME_URL = reverse('worktime-list')


class PublicWorkTimesApiTests(TestCase):
    """Test the publicly available workTimes API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(WORKTIME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_work_time_without_authentication_should_fail(self):
        """Test that login is required to create a new workTime"""
        payload = {}
        res = self.client.post(WORKTIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)




class PrivateWorkTimesApiTests(TestCase):
    """Test the private workTimes API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '123qwe'
        )
        self.client.force_authenticate(self.user)

    def test_create_work_time_not_allowed(self):
        """Test accessing the create workTime endpoint"""
        payload = {}
        res = self.client.post(WORKTIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
