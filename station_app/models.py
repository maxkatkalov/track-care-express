from django.db import models
from django.conf import settings


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


class Train(models.Model):
    name = models.CharField(max_length=100)
    carriage_num = models.IntegerField()
    places_in_carriage = models.IntegerField()
    train_type = models.ForeignKey(
        "TrainType", on_delete=models.CASCADE, related_name="trains"
    )

    def __str__(self) -> str:
        return f"Train: {self.name}, type: {self.train_type}"


class TrainType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    staff_member_since = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Crew member: {self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="journeys"
    )
    train = models.ForeignKey(
        Train, on_delete=models.CASCADE, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self) -> str:
        return (
            f"Journey: {self.route} - {self.train}: "
            f"{self.departure_time} - {self.arrival_time}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    def __str__(self) -> str:
        return f"Order: {self.created_at}"


class Ticket(models.Model):
    carriage = models.IntegerField()
    seat = models.IntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self) -> str:
        return f"Ticket: {self.order} - {self.journey}"