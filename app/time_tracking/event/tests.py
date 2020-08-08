from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.event.models import Event


EVENTS_URL = reverse('event-list')


class PublicEventsApiTests(TestCase):
    """Test the publicly available events API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_not_required(self):
        """Test that login is not required to access the endpoint"""
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_event_without_authentication_should_fail(self):
        """Test that login is required to create a new event"""
        payload = {
            'title': 'test title',
            'start_time': '2020-09-10T06:00:00Z',
            'end_time': '2020-10-15T13:33:45Z'
        }
        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEventsApiTests(TestCase):
    """Test the private events API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '123qwe'
        )
        self.client.force_authenticate(self.user)

    def test_create_event_successful(self):
        """Test create a new event"""
        payload = {
            'title': 'test title',
            'start_date': '2020-09-10',
            'end_date': '2020-10-15'
        }
        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Event.objects.filter(
            title=payload['title'],
        ).exists()
        self.assertTrue(exists)
