from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime
from time_tracking.work_time.serializers import WorkTimeSerializer

WORK_TIME_URL = reverse('worktime-list')


def detail_url(work_time_id):
    """Return event detail URL"""
    return reverse('worktime-detail', args=[work_time_id])


def sample_work_time(user, **params):
    """Create and return a sample WorkTime"""
    time_now = timezone.now()
    defaults = {
        'start_datetime': time_now + timedelta(days=-1),
        'end_datetime': time_now + timedelta(days=-1) + timedelta(minutes=480, microseconds=555),
    }
    defaults.update(params)
    wt = WorkTime.objects.create(owner=user, **defaults)
    wt.save()
    return wt


class PublicWorkTimesApiTests(TestCase):
    """Test the publicly available workTimes API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(WORK_TIME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_work_time_without_authentication_should_fail(self):
        """Test that login is required to create a new workTime"""
        payload = {}
        res = self.client.post(WORK_TIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWorkTimesApiTests(TestCase):
    """Test the private workTimes API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test-user'
            'test@test.com',
            '123qwe',
            is_staff=False,
        )
        self.client.force_authenticate(self.user)
        self.other_user = get_user_model().objects.create_user(
            'test-other-user'
            'other@test.com',
            '123qwe',
            is_staff=False,
        )

    def test_create_checkin_successful(self):
        """Test create a new check-in"""
        payload = {'start_datetime': timezone.now()}
        res = self.client.post(WORK_TIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = WorkTime.objects.filter(
            start_datetime=payload['start_datetime'],
            end_datetime__isnull=True,
            owner=self.user,
        ).exists()
        self.assertTrue(exists, "data should be persisted in the db")

    def test_create_checkin_and_checkout_successful(self):
        """Test create a new check-in and check-out"""
        payload = {'start_datetime': timezone.now(), 'end_datetime': timezone.now()}
        res = self.client.post(WORK_TIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = WorkTime.objects.filter(
            start_datetime=payload['start_datetime'],
            end_datetime=payload['end_datetime'],
            owner=self.user,
        ).exists()
        self.assertTrue(exists, "data should be persisted in the db")

    def test_create_checkin_while_checked_in(self):
        """
        Test create a new check-in while the old check-in doesn't have checkout
        """
        sample_work_time(self.user, end_datetime=None)
        payload = {'start_datetime': timezone.now()}
        res = self.client.post(WORK_TIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieving_work_times(self):
        """Test retrieving the workTime for the user"""
        work_time = sample_work_time(self.user)
        res = self.client.get(WORK_TIME_URL)
        wts = WorkTimeSerializer(data=res.data['results'][0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

        self.assertTrue(wts.is_valid(), f"validate the resulted data isn't correct {wts.errors}")
        self.assertEqual(res.data['results'][0]['id'], work_time.id)
        self.assertEqual(
            wts.validated_data['start_datetime'],
            work_time.start_datetime
        )
        self.assertEqual(
            wts.validated_data['end_datetime'],
            work_time.end_datetime
        )

    def test_retrieving_work_times_for_different_owner(self):
        """Test retrieving the workTime shouldn't include other users Times"""
        sample_work_time(self.other_user)
        res = self.client.get(WORK_TIME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)

    def test_create_should_fail_when_checkout_is_after_checkout_time(self):
        """
        Test creating a workTime should fail\
         where the checkin time is after the checkout time
        """
        payload = {'start_datetime': timezone.now(), 'end_datetime': timezone.now() - timedelta(hours=5)}

        res = self.client.post(WORK_TIME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_should_fail_when_checkout_is_after_checkout_time(self):
        """
        Test updating a workTime should fail\
         where the checkin time is after the checkout time
        """
        work_time = sample_work_time(self.user, end_datetime=None)
        url = detail_url(work_time.id)
        payload = {'end_datetime': work_time.start_datetime - timedelta(hours=5)}

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
