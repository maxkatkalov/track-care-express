from django.urls import reverse

from station_app.models import Station


STATIONS_LIST_URL = reverse("station_app:stations-list")

STATION_PAYLOAD = {
            "name": "Sample station",
            "latitude": 500,
            "longitude": -500,
        }


def sample_station(count: int = 1, **params):
    defaults = {
        "name": "Sample station",
        "latitude": 500,
        "longitude": -500,
    }
    defaults.update(params)

    if count > 1:
        for station_num in range(1, count + 1):
            Station.objects.create(
                name=f"Sample station {station_num}",
                latitude=defaults["latitude"],
                longitude=defaults["longitude"],
            )
        return
    return Station.objects.create(**defaults)


def station_detail_url(station_pk: int = 1):
    return reverse("station_app:stations-detail", args=[station_pk])