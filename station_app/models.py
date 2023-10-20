from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return f"Station: {self.name}: {self.latitude}, {self.longitude}"


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes"
    )
    distance = models.FloatField()

    def __str__(self) -> str:
        return f"Route: {self.source} - {self.destination}: {self.distance}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="journeys"
    )
    train = models.ForeignKey(
        "Train", on_delete=models.CASCADE, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self) -> str:
        return (
            f"Journey: {self.route} - {self.train}: "
            f"{self.departure_time} - {self.arrival_time}"
        )
