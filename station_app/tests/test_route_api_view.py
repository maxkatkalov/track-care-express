from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from station_app.models import Route, Station
from station_app.serializers import RouteSerializer
from .samples import (
    ROUTES_LIST_URL,
    sample_station,
)


class AuthenticatedStationTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        sample_station(2)
        station1 = Station.objects.get(pk=1)
        station2 = Station.objects.get(pk=2)

        Route.objects.create(source=station1, destination=station2, distance=100)
        Route.objects.create(source=station2, destination=station1, distance=100)

        response = self.client.get(ROUTES_LIST_URL)

        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(routes.count(), len(serializer.data))
        self.assertEqual(response.data, serializer.data)
