from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

URLS = {
    "station_app_urls": (
        reverse("station_app:stations-list"),
        reverse("station_app:routes-list"),
        reverse("station_app:trains-list"),
        reverse("station_app:trains-type-list"),
        reverse("station_app:crew-list"),
        reverse("station_app:journeys-list"),
        reverse("station_app:tickets-list"),
    ),
    "station_user_urls": {
        "register": reverse("station_user:create"),
        "login": reverse("station_user:token_obtain_pair"),
        "refresh_token": reverse("station_user:token_refresh"),
    },
}


class UnauthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        for url in URLS.get("station_app_urls"):
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

    def test_authenticated_can_register_and_login(self):
        data_new_user = {
            "email": "a@b.com",
            "password": "test1234",
        }
        response_register = self.client.post(
            URLS.get("station_user_urls").get("register"),
            data_new_user,
        )
        response_login = self.client.post(
            URLS.get("station_user_urls").get("login"), data_new_user
        )

        self.assertEqual(
            response_register.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {"email": "a@b.com", "password": "test1234"}
        self.user = get_user_model().objects.create_user(
            email=self.user_data.get("email"),
            password=self.user_data.get("password"),
        )
        self.client.force_authenticate(user=self.user)

    def test_auth_not_required(self):
        for url in URLS.get("station_app_urls"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_can_refresh_token(self):
        response_login = self.client.post(
            URLS.get("station_user_urls").get("login"), self.user_data
        )
        refresh_token = response_login.data.get("refresh")
        response_refresh = self.client.post(
            URLS.get("station_user_urls").get("refresh_token"),
            {"refresh": refresh_token},
        )

        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
