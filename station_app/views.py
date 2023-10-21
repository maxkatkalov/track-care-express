from rest_framework.viewsets import ModelViewSet

from .models import Station, Route
from .serializers import (
    StationSerializer,
    StationDetailSerializer,
    RouteSerializer,
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
