import uuid
from datetime import datetime
import os
from django.utils.text import slugify

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    distance = models.FloatField()

    @staticmethod
    def validate_route(
        source,
        destination,
        error_to_raise=ValidationError,
    ):
        if source == destination or destination == source:
            raise error_to_raise(
                {
                    "source": [
                        "source and destination cannot be the same station"
                    ]
                }
            )

    def clean(self):
        Route.validate_route(self.source, self.destination, ValidationError)

    def save(
        self, *args, **kwargs
    ):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Route: {self.source.name} " f"- {self.destination.name}."


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


def crew_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/crew/", filename)


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    staff_member_since = models.DateField(auto_now_add=True)
    profile_image = models.ImageField(null=True, upload_to=crew_image_file_path)

    @property
    def full_name(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


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

    @staticmethod
    def validate_journey_date_times_fields(
        departure_time: datetime,
        arrival_time: datetime,
        error_to_raise: ValidationError,
    ) -> None:
        if departure_time >= arrival_time:
            raise error_to_raise(
                {
                    "source_datetime": [
                        "source_datetime cannot be later than or equal to arrival_time"
                    ]
                }
            )
        if departure_time < timezone.now():
            raise error_to_raise(
                {
                    "departure_time": [
                        f"departure_time cannot be in the past it should be after {datetime.now().strftime('%Y-%m-%d, %H:%M')}"
                    ]
                }
            )

    def clean(self):
        Journey.validate_journey_date_times_fields(
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            error_to_raise=ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

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
                        f"range: (1, {train.carriage_num})"
                    ]
                }
            )
        elif not 1 <= seat <= train.places_in_carriage:
            raise error_to_raise(
                {
                    "seat": [
                        f"seat number must be in available range: "
                        f"(1, {train.places_in_carriage})"
                    ]
                }
            )

    def clean(self):
        Ticket.validate_ticket(
            self.carriage,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Ticket: {self.order} - {self.journey}"

    class Meta:
        unique_together = ("journey", "carriage", "seat")
        ordering = ["carriage", "seat"]
