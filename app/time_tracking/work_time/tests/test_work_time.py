from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.test import APIClient

from time_tracking.work_time.models import WorkTime, convert_time_to_unix
from time_tracking.work_time.serializers import (
    convert_unix_to_time,
    convert_unix_to_datetime,
)

WORK_TIME_URL = reverse('worktime-list')


def sample_work_time(user, **params):
    """Create and return a sample WorkTime"""
    time_now = timezone.now()
    yesterday_datetime = datetime(
        time_now.year, time_now.month, time_now.day
    ) + timedelta(days=-1)
    defaults = {
        'start_date': yesterday_datetime.date(),
        'unix_start_time': convert_time_to_unix(yesterday_datetime),
        'unix_end_time': convert_time_to_unix(
            yesterday_datetime + timedelta(minutes=480)
        ),
    }
    defaults.update(params)
    wt = WorkTime.objects.create(owner=user, **defaults)
    wt.save()
    wt.unix_start_time = defaults['unix_start_time']
    wt.start_date = defaults['start_date']
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

    def test_create_work_time_not_allowed(self):
        """Test accessing the create workTime endpoint"""
        payload = {}
        res = self.client.post(WORK_TIME_URL, payload)

        self.assertEqual(
            res.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_retrieving_work_times(self):
        """Test retrieving the workTime for the user"""
        work_time = sample_work_time(self.user)
        res = self.client.get(WORK_TIME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], work_time.id)
        self.assertEqual(
            res.data[0]['start_datetime'],
            convert_unix_to_datetime(
                work_time.start_date,
                work_time.unix_start_time
            )
        )
        self.assertEqual(
            res.data[0]['end_datetime'],
            convert_unix_to_datetime(
                work_time.start_date,
                work_time.unix_end_time
            )
        )

    def test_retrieving_work_times_for_different_owner(self):
        """Test retrieving the workTime shouldn't include other users Times"""
        sample_work_time(self.other_user)
        res = self.client.get(WORK_TIME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_the_convert_unix_to_time_function(self):
        """Test that the function convert_unix_to_time convert correctly"""
        time_now = timezone.now()

        sut = convert_unix_to_time(time_now.timestamp())

        self.assertEqual(time_now.time(), sut)

    def test_the_convert_unix_to_datetime_function(self):
        """Test that the function convert_unix_to_datetime convert correctly"""
        datetime_now = timezone.now()
        date_now = datetime_now.date()
        today_seconds_count = convert_time_to_unix(datetime_now.time())

        sut = convert_unix_to_datetime(date_now, today_seconds_count)

        self.assertGreaterEqual(sut, datetime_now - timedelta(seconds=1))
        self.assertLessEqual(sut, datetime_now + timedelta(seconds=1))

    def test_the_convert_time_to_unix_function(self):
        """Test that the function convert_time_to_unix convert correctly"""
        time_now = timezone.now()
        seconds = (time_now.hour * 60 + time_now.minute) * 60 + time_now.second

        sut = convert_time_to_unix(time_now)

        self.assertEqual(sut, seconds)

    def test_unix_start_time_field_should_auto_populate_on_create(self):
        """
        Test that unix_start_time takes the now time automatically on create
        """
        unix_time_now = convert_time_to_unix(timezone.now())
        wt = WorkTime.objects.create(owner=self.user)

        self.assertGreaterEqual(wt.unix_start_time, unix_time_now)
        self.assertLessEqual(wt.unix_start_time, unix_time_now + 10)
