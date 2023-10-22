from rest_framework.viewsets import ModelViewSet
from django.db.models import Count, F

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
    JoureyDetailSerializer,
    OrderSerializer,
    TicketSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
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
    queryset = Journey.objects.annotate(
            tickets_available=(
                F("train__carriage_num") * F("train__places_in_carriage")
                - Count("tickets")
            )
        )
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JoureyDetailSerializer
        return JourneySerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.annotate(
        total_tickets=Count("tickets")
    )
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
