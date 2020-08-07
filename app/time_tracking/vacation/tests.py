from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.vacation.models import Vacation
from time_tracking.vacation.serializers import VacationSerializer


VACATION_URL = reverse('vacation-list')


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
        payload = {'title': 'test title', 'start_date': '2020-09-10', 'number_of_days': '18'}
        res = self.client.post(VACATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)




class PrivateVacationsApiTests(TestCase):
    """Test the private vacations API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '123qwe'
        )
        self.client.force_authenticate(self.user)

    def test_create_event_successful(self):
        """Test create a new Vacation"""
        payload = {'brief_description': 'test brief description', 'start_date': '2020-09-10', 'number_of_days': '2'}
        res = self.client.post(VACATION_URL, payload)

        exists = Vacation.objects.filter(
            brief_description=payload['brief_description'],
            start_date=payload['start_date'],
            number_of_days=payload['number_of_days'],
            owner=self.user,
        ).exists()
        self.assertTrue(exists)
