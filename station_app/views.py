from rest_framework.viewsets import ModelViewSet

from .models import Station, Route, Train, TrainType
from .serializers import (
    StationSerializer,
    StationDetailSerializer,
    RouteSerializer,
    TrainSerializer,
    TrainTypeSerializer,
    TrainDetailSerializer,
    TrainListSerializer,
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
