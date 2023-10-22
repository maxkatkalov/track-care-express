from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from station_app.models import Station
from station_app.serializers import StationSerializer, StationDetailSerializer

from .samples import (
    sample_station,
    station_detail_url,
    STATION_PAYLOAD,
    STATIONS_LIST_URL
)


class AuthenticatedStationTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_correct_get_serializer_class_return(self):
        sample_station(2)

        response_list = self.client.get(STATIONS_LIST_URL)
        response_single = self.client.get(station_detail_url(2))

        view_list = response_list.renderer_context["view"]
        view_single = response_single.renderer_context["view"]

        self.assertEqual(view_list.get_serializer_class(), StationSerializer)
        self.assertEqual(view_single.get_serializer_class(), StationDetailSerializer)

    def test_list_stations(self):
        sample_station(2)

        response = self.client.get(STATIONS_LIST_URL)

        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(stations.count(), len(serializer.data))
        self.assertEqual(response.data, serializer.data)

    def test_detail_station(self):
        sample_station()

        response = self.client.get(station_detail_url())
        station = Station.objects.get(pk=1)
        serializer = StationDetailSerializer(station)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_station_forbidden(self):
        response = self.client.post(STATIONS_LIST_URL, STATION_PAYLOAD)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_station_forbidden(self):
        sample_station()

        response = self.client.put(
            station_detail_url(),
            STATION_PAYLOAD,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_station_forbidden(self):
        sample_station()

        response = self.client.delete(station_detail_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserStationTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_create_station_allow(self):
        response = self.client.post(STATIONS_LIST_URL, STATION_PAYLOAD)
        created_station = Station.objects.get(pk=1)
        serializer = StationSerializer(created_station)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_update_station_allow(self):
        sample_station(name="Sample station 2")

        station_before_update = Station.objects.get(pk=1)
        serializer_before = StationSerializer(station_before_update)

        response = self.client.put(
            station_detail_url(),
            STATION_PAYLOAD,
        )

        station_after_update = Station.objects.get(pk=1)
        serializer_after = StationSerializer(station_after_update)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEquals(serializer_before.data, serializer_after.data)
        self.assertEqual(response.data, serializer_after.data)

    def test_delete_station_allow(self):
        sample_station()

        response = self.client.delete(station_detail_url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
