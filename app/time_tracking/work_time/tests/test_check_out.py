from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime


CHECK_OUT_URL = reverse('worktime-checkout-list')


class PublicCheckOutsApiTests(TestCase):
    """Test the publicly available checkOuts API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(CHECK_OUT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_checkout_without_authentication_should_fail(self):
        """Test that login is required to create a new checkOut"""
        payload = {}
        res = self.client.post(CHECK_OUT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCheckOutsApiTests(TestCase):
    """Test the private checkOuts API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '123qwe'
        )
        self.client.force_authenticate(self.user)

    def test_create_checkout_successful(self):
        """Test create a new checkOut"""
        work_time = WorkTime(owner=self.user)
        work_time.save()
        payload = {}
        res = self.client.post(CHECK_OUT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = WorkTime.objects.filter(
            start_time__isnull=False,
            end_time__isnull=False,
            owner=self.user,
        ).exists()
        self.assertTrue(exists)
