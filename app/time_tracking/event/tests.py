from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.event.models import Event


EVENTS_URL = reverse('event-list')
VALID_PAYLOAD = {
    'title': 'school visit day',
    'description': '''Lorem ipsum dolor sit amet, consectetur adipiscing
    ipsum sit amet tortor varius placerat. Quisque justo nisi, ultricies nec
    iaoreet sed, lacinia nec ante. Vivamus vehicula faucibus neque vel vehicula
    Ut consectetur lectus ac dolor imperdiet, vestibulum ex ultrices. In mattis
    placerat dictum. Etiam imperdiet nec dolor a convallis. Nullam vitae dolor
    consequat, feugiat nulla eget, porta libero. Suspendisse potenti.''',
    'start_date': '2020-09-10',
    'end_date': '2020-10-15'
}


def detail_url(event_id):
    """Return event detail URL"""
    return reverse('event-detail', args=[event_id])


def sample_event(user, **params):
    """Create and return a sample event"""
    defaults = {
        'title': 'Sample event',
        'description': 'Sample event description',
        'start_date': '2020-09-1',
        'end_date': '2020-9-2'
    }
    defaults.update(params)

    return Event.objects.create(created_by=user, **defaults)


class PublicEventsApiTests(TestCase):
    """Test the publicly available events API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_not_required(self):
        """Test that login is not required to access the endpoint"""
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_event_unauthorized(self):
        """Test that login is required to create a new event"""
        res = self.client.post(EVENTS_URL, VALID_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        exists = Event.objects.all().exists()
        self.assertFalse(exists)


class StaffUsersEventsApiTests(TestCase):
    """Test staff members events API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user',
            'test@test.com',
            '123qwe',
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_event_successful(self):
        """Test create a new event"""
        res = self.client.post(EVENTS_URL, VALID_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Event.objects.filter(
            title=VALID_PAYLOAD['title'],
            description=VALID_PAYLOAD['description'],
            start_date=VALID_PAYLOAD['start_date'],
            end_date=VALID_PAYLOAD['end_date']
        ).exists()
        self.assertTrue(exists)

    def test_full_update_event_successful(self):
        """Test update an event"""
        event = sample_event(user=self.user)
        url = detail_url(event.id)
        start_date = datetime.strptime(event.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(event.end_date, '%Y-%m-%d').date()
        payload = {
            'title': event.title + '-new title',
            'description': event.description + 'new description',
            'start_date': start_date + timedelta(days=2),
            'end_date': end_date + timedelta(days=5),
        }

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, payload['title'])
        self.assertEqual(event.description, payload['description'])
        self.assertEqual(event.start_date, payload['start_date'])
        self.assertEqual(event.end_date, payload['end_date'])

    def test_partially_update_event_successful(self):
        """Test partially update an event"""
        event = sample_event(user=self.user)
        url = detail_url(event.id)
        payload = {
            'title': event.title + '-new title',
        }

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, payload['title'])

    def test_delete_event(self):
        """Test delete an event"""
        event = sample_event(user=self.user)
        url = detail_url(event.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Event.objects.all().exists()
        self.assertFalse(exists)

    def test_create_event_with_end_date_before_the_start_date(self):
        """Test create an event where the start date is after the end date"""
        payload = {
            'title': 'event title',
            'start_date': '2020-5-5',
            'end_date': '2020-1-1',
        }

        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class NonStaffUsersRequestsEventsApiTests(TestCase):
    """Test non-staff members events API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user',
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_create_event_forbidden(self):
        """Test create a new event with unauthorized user"""
        res = self.client.post(EVENTS_URL, VALID_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        exists = Event.objects.all().exists()
        self.assertFalse(exists)

    def test_full_update_event_forbidden(self):
        """Test update an event with unauthorized user"""
        event = sample_event(user=self.user)
        url = detail_url(event.id)
        start_date = datetime.strptime(event.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(event.end_date, '%Y-%m-%d').date()
        payload = {
            'title': event.title + '-new title',
            'description': event.description + '-new description',
            'start_date': start_date + timedelta(days=2),
            'end_date': end_date + timedelta(days=5),
        }

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partially_update_event_unauthorized(self):
        """Test partially-update an event with unauthorized user"""
        event = sample_event(user=self.user)
        url = detail_url(event.id)
        payload = {
            'title': event.title + '-new title'
        }

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_unauthorized(self):
        """Test delete an event with unauthorized user"""
        event = sample_event(user=self.user)
        url = detail_url(event.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
