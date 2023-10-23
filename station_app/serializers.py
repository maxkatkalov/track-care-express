from rest_framework import serializers
from django.db import transaction


from .models import (
    Station,
    Route,
    Train,
    TrainType,
    Crew,
    Journey,
    Order,
    Ticket,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class StationDetailSerializer(serializers.ModelSerializer):
    # five_departing_source_for = serializers.SerializerMethodField()
    # five_incoming_destination_for = serializers.SerializerMethodField()

    @staticmethod
    def get_five_departing_source_for(obj):
        sources = Route.objects.filter(source=obj).order_by(
            "-source_datetime"
        )[:5]
        return [str(source) for source in sources]

    @staticmethod
    def get_five_incoming_destination_for(obj):
        destinations = Route.objects.filter(destination=obj).order_by(
            "-destination_datetime"
        )[:5]
        return serializers.StringRelatedField(
            many=True, read_only=True
        ).to_representation(destinations)

    class Meta:
        model = Station
        fields = (
            "id",
            "name",
            "latitude",
            "longitude",
            # "five_departing_source_for",
            # "five_incoming_destination_for",
        )


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Route.validate_route(
            data["source"],
            data["destination"],
            serializers.ValidationError,
        )
        return data

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewDetailSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name", "profile_image", "staff_member_since")


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "profile_image")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "train_type",
            "carriage_num",
            "places_in_carriage",
            "train_type",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.StringRelatedField()


class TrainDetailSerializer(TrainListSerializer):
    train_type_link = serializers.HyperlinkedRelatedField(
        source="train_type",
        view_name="station_app:trains-type-detail",
        read_only=True,
    )

    class Meta(TrainSerializer.Meta):
        fields = TrainSerializer.Meta.fields + ("train_type_link",)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class OrderField(serializers.PrimaryKeyRelatedField):
    """To show only request.user orders on TicketSerializer order field"""

    def get_queryset(self):
        user = self.context["request"].user
        return Order.objects.filter(user=user)


class TicketSerializer(serializers.ModelSerializer):
    journey = serializers.PrimaryKeyRelatedField(
        queryset=Journey.objects.select_related(
            "route",
            "route__source",
            "route__destination",
            "train",
            "train__train_type",
        )
    )

    class Meta:
        model = Ticket
        fields = ("id", "carriage", "seat", "journey")

    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Ticket.validate_ticket(
            data["carriage"],
            data["seat"],
            data.get("journey").train,
            serializers.ValidationError,
        )
        return data


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("carriage", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.created_at = validated_data.get(
                "created_at", instance.created_at
            )
            instance.save()

            tickets_data = validated_data.get("tickets", [])
            ticket_ids = [ticket.get("id") for ticket in tickets_data]

            tickets_to_delete = instance.tickets.exclude(id__in=ticket_ids)
            tickets_to_delete.delete()

            for ticket_data in tickets_data:
                ticket_id = ticket_data.get("id")
                if ticket_id:
                    ticket = instance.tickets.filter(id=ticket_id).first()
                    if ticket:
                        ticket.some_field = ticket_data.get("some_field")
                        ticket.save()
                else:
                    Ticket.objects.create(order=instance, **ticket_data)

        return instance


class JourneySerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination")
    )
    train = serializers.PrimaryKeyRelatedField(
        queryset=Train.objects.select_related("train_type")
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
        )

    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Journey.validate_journey_date_times_fields(
            data["departure_time"],
            data["arrival_time"],
            serializers.ValidationError,
        )
        return data


class JourneyListSerializer(JourneySerializer):
    route_link = serializers.HyperlinkedRelatedField(
        source="route", view_name="station_app:routes-detail", read_only=True
    )
    train_link = serializers.HyperlinkedRelatedField(
        source="train", view_name="station_app:trains-detail", read_only=True
    )
    source = serializers.SlugRelatedField(
        source="route.source", read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        source="route.destination", read_only=True, slug_field="name"
    )

    class Meta(JourneySerializer.Meta):
        fields = JourneySerializer.Meta.fields + (
            "route_link",
            "train_link",
            "source",
            "destination",
        )


class JoureyDetailSerializer(JourneyListSerializer):
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Journey
        fields = JourneyListSerializer.Meta.fields + ("taken_places",)


class OrderListSerializer(serializers.ModelSerializer):
    tickets = serializers.HyperlinkedRelatedField(
        many=True, view_name="station_app:tickets-detail", read_only=True
    )
    total_tickets = serializers.IntegerField()

    class Meta:
        model = Order
        fields = OrderSerializer.Meta.fields + ("total_tickets",)


class OrderDetailSerializer(OrderListSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    tickets_link = serializers.HyperlinkedRelatedField(
        source="tickets",
        many=True,
        read_only=True,
        view_name="station_app:tickets-detail",
    )

    class Meta:
        model = Order
        fields = OrderListSerializer.Meta.fields + ("tickets_link",)
