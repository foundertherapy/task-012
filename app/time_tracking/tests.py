from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


TOKEN_AUTH_URL = reverse('api-token-auth')


class TokenAuthenticationApiTests(TestCase):
    """Test the users can get the token from the API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@test.com',
            password='123qwe'
        )
        self.client.force_authenticate(self.user)

    def test_invalid_parameters_should_not_return_a_token(self):
        """
        Test that the endpoint will return error when user password is invalid
        """
        payload = {"username": self.user.username, "password": "x123qwe"}
        res = self.client.post(TOKEN_AUTH_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_with_valid_user_should_return_valid_token(self):
        """
        Test that the endpoint will return a valid token to the valid user
        """
        payload = {"username": self.user.username, "password": "123qwe"}
        res = self.client.post(TOKEN_AUTH_URL, payload)
        token = Token.objects.get_or_create(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['token'] in str(token))
