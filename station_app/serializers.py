from rest_framework import serializers

from .models import (
    Station,
    Route,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class StationDetailSerializer(serializers.ModelSerializer):
    five_departing_source_for = serializers.SerializerMethodField()
    five_incoming_destination_for = serializers.SerializerMethodField()

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
            "five_departing_source_for",
            "five_incoming_destination_for",
        )


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Route.validate_route(
            data["source"],
            data["destination"],
            data.get("source_datetime"),
            data.get("destination_datetime"),
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
            "source_datetime",
            "destination_datetime",
        )
