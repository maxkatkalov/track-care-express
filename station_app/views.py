from rest_framework.viewsets import ModelViewSet

from .models import Station, Route, Train, TrainType, Crew, Journey
from .serializers import (
    StationSerializer,
    StationDetailSerializer,
    RouteSerializer,
    TrainSerializer,
    TrainTypeSerializer,
    TrainDetailSerializer,
    TrainListSerializer,
    CrewSerializer,
    JourneySerializer,
    JourneyListSerializer,
)


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StationDetailSerializer
        return StationSerializer


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class CrewViewSet(ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class TrainViewSet(ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TrainDetailSerializer
        if self.action == "list":
            return TrainListSerializer

        return TrainSerializer


class TrainTypeViewSet(ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        return JourneySerializer
