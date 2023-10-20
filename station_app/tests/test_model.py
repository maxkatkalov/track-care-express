import django
django.setup()
from django.test import TestCase

from station_app.models import Station


class StationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_station = Station.objects.create(
            name="Test Station",
            latitude=37.7749,
            longitude=-122.4194
        )
        cls.name_field = Station._meta.get_field("name")
        cls.latitude_field = Station._meta.get_field("latitude")
        cls.longitude_field = Station._meta.get_field("longitude")

    def test_name_field_labels(self):
        self.assertEqual(
            self.name_field.verbose_name,
            "name"
        )
        self.assertEqual(
            self.latitude_field.verbose_name,
            "latitude"
        )
        self.assertEqual(
            self.longitude_field.verbose_name,
            "longitude"
        )

    def test_name_max_length(self):
        self.assertEqual(
            self.name_field.max_length,
            100
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.test_station),
            "Station: Test Station: 37.7749, -122.4194"
        )
