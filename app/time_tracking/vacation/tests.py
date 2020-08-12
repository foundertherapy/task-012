from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.vacation.models import Vacation
from time_tracking.event.models import Event


VACATION_URL = reverse('vacation-list')


def detail_url(vacation_id):
    """Return vacation detail URL"""
    return reverse('vacation-detail', args=[vacation_id])


def get_future_year_starting_date(add_years=2):
    """
    calculates the date at the beginning of the next second year

    :return: datetime.date
    """
    return date(timezone.now().date().year + add_years, 1, 1)


def sample_vacation(user, add_years=0, **params):
    """Create and return a sample event"""
    defaults = {
        'brief_description': 'Sample vacation brief description',
        'start_date': get_future_year_starting_date(add_years),
        'number_of_days': 1
    }
    defaults.update(params)

    return Vacation.objects.create(owner=user, **defaults)


class PublicVacationsApiTests(TestCase):
    """Test the publicly available Vacations API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(VACATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_a_vacation_without_authentication_should_fail(self):
        """Test that login is required to create a new Vacations"""
        payload = {
            'brief_description': 'test title',
            'start_date': get_future_year_starting_date(),
            'number_of_days': 18
        }
        res = self.client.post(VACATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVacationsApiTests(TestCase):
    """Test the private vacations API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_create_event_successful(self):
        """Test create a new Vacation"""
        payload = {
            'brief_description': 'test brief description',
            'start_date': get_future_year_starting_date() + timedelta(days=1),
            'number_of_days': 2
        }

        res = self.client.post(VACATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Vacation.objects.filter(
            brief_description=payload['brief_description'],
            start_date=payload['start_date'],
            number_of_days=payload['number_of_days'],
            owner=self.user,
        ).exists()
        self.assertTrue(exists)

    def test_add_more_than_16_days_with_one_request(self):
        """Test request with more than 16 days vacation should fail"""
        payload = {
            'brief_description': 'test brief description',
            'start_date': get_future_year_starting_date() + timedelta(days=1),
            'number_of_days': 17
        }

        res = self.client.post(VACATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_more_than_16_days_with_two_requests(self):
        """
        Test requests with a result sum more than 16 days with in\
        the same year should fail
        """
        payload1 = {
            'brief_description': 'test brief description 1',
            'start_date': get_future_year_starting_date() + timedelta(days=1),
            'number_of_days': 12
        }
        payload2 = {
            'brief_description': 'test brief description 2',
            'start_date': get_future_year_starting_date() + timedelta(days=14),
            'number_of_days': 5
        }

        res1 = self.client.post(VACATION_URL, payload1)
        res2 = self.client.post(VACATION_URL, payload2)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("can't add more than 4 day", res2.data.get('detail'))

    def test_add_vacation_days_when_last_year_vacations_are_full(self):
        """
        Test requests with less than 17 vacation days while the vacations\
        before that year are fully taken.
        """
        sample_vacation(self.user, add_years=-1, number_of_days=16)
        payload = {
            'brief_description': 'test brief description',
            'start_date': timezone.now().date(),
            'number_of_days': 16
        }

        res = self.client.post(VACATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_full_update_vacation_successful(self):
        """Test update a vacation description"""
        vacation = sample_vacation(user=self.user)
        url = detail_url(vacation.id)
        payload = {
            'brief_description': vacation.brief_description + '-new update',
            'start_date': vacation.start_date,
            'number_of_days': vacation.number_of_days,
        }

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        vacation.refresh_from_db()
        self.assertEqual(vacation.brief_description,
                         payload['brief_description'])
        self.assertEqual(vacation.start_date, payload['start_date'])
        self.assertEqual(vacation.number_of_days, payload['number_of_days'])

    def test_partially_update_event_successful(self):
        """Test partially update a vacation"""
        vacation = sample_vacation(user=self.user)
        url = detail_url(vacation.id)
        payload = {
            'brief_description': vacation.brief_description + '-new update',
        }

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        vacation.refresh_from_db()
        self.assertEqual(vacation.brief_description,
                         payload['brief_description'])

    def test_delete_future_vacation_successful(self):
        """Test delete a future vacation"""
        vacation = sample_vacation(user=self.user, add_years=1)
        url = detail_url(vacation.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_an_old_vacation_should_fail(self):
        """Test delete an old vacation is forbidden"""
        vacation = sample_vacation(user=self.user, add_years=-1)
        url = detail_url(vacation.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateVacationsWithEventsApiTests(TestCase):
    """Test the private vacations while having events API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)

    def test_add_vacation_on_the_same_day_as_an_event(self):
        """Test add a vacation that intersects with an event"""
        payload = {
            'brief_description': 'test brief description',
            'start_date': timezone.now().date(),
            'number_of_days': 16
        }
        event = {
            'title': 'school visit day',
            'start_date': payload['start_date'],
            'end_date': payload['start_date']
        }
        event = Event.objects.create(created_by=self.user, **event)

        res = self.client.post(VACATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertTrue(len(res.data.get('events_urls')) == 1)
