from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return f"Station: {self.name}: {self.latitude}, {self.longitude}"


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="source_rout_station"
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="destination_rout_station",
    )
    source_datetime = models.DateTimeField(default=datetime.now)
    destination_datetime = models.DateTimeField(
        default=(datetime.now() + timedelta(days=1))
    )
    distance = models.FloatField()

    @staticmethod
    def validate_route(
        source,
        destination,
        source_datetime,
        destination_datetime,
        error_to_raise=ValidationError,
    ):
        if source == destination:
            raise error_to_raise(
                {
                    "source": [
                        "source and destination cannot be the same station"
                    ]
                }
            )
        elif source_datetime >= destination_datetime:
            raise error_to_raise(
                {
                    "source_datetime": [
                        "source_datetime cannot be later than or equal to destination_datetime"
                    ]
                }
            )

    def clean(self):
        Route.validate_route(
            self.source,
            self.destination,
            self.source_datetime,
            self.destination_datetime,
            ValidationError
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return (
            f"Route: {self.source.name} {self.source_datetime.strftime('%Y-%m-%d, %H:%M')} "
            f"- {self.destination.name}: {self.source_datetime.strftime('%Y-%m-%d, %H:%M')}"
        )


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
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self) -> str:
        return (
            f"Journey: {self.route} - {self.train}: "
            f"{self.departure_time} - {self.arrival_time}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
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

    @staticmethod
    def validate_ticket(carriage, seat, train, error_to_raise):
        if not 1 <= carriage <= train.carriage_num:
            raise error_to_raise(
                {
                    "carriage": [
                        f"carriage number must be in available "
                        f"range: (1, carriage): "
                        f"(1, {train.carriage_num})"
                    ]
                }
            )
        elif not 1 <= seat <= train.places_in_carriage:
            raise error_to_raise(
                {
                    "seat": [
                        f"seat number must be in available range: "
                        f"(1, seats_in_row): "
                        f"(1, {train.places_in_carriage})"
                    ]
                }
            )

    def clean(self):
        Ticket.validate_ticket(
            self.carriage,
            self.seat,
            self.journey.train.carriage_num,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"Ticket: {self.order} - {self.journey}"

    class Meta:
        unique_together = ("carriage", "carriage", "seat")
        ordering = ["carriage", "seat"]
