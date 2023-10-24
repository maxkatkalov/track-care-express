from datetime import datetime

from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

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
    CrewImageSerializer,
    CrewDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JoureyDetailSerializer,
    OrderSerializer,
    TicketSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)
from .permissions import IsAdminOrIfAuthenticatedReadOnly


class DefaultSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = DefaultSetPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StationDetailSerializer
        return self.serializer_class


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            return self.queryset.select_related("source", "destination")
        return self.queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = DefaultSetPagination

    def get_serializer_class(self):
        if self.action == "upload_image":
            return CrewImageSerializer
        if self.action == "retrieve":
            return CrewDetailSerializer
        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific crew member"""
        crew_member = self.get_object()
        serializer = self.get_serializer(crew_member, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            return self.queryset.select_related("train_type")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TrainDetailSerializer
        if self.action == "list":
            return TrainListSerializer

        return self.serializer_class


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = DefaultSetPagination


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related(
            "route__source",
            "route__destination",
        )
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("train__carriage_num") * F("train__places_in_carriage")
                - Count("tickets")
            )
        )
    )
    serializer_class = JourneySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        queryset = self.queryset
        if source_station := self.request.query_params.get("source"):
            queryset = queryset.filter(
                route__source__name__icontains=source_station
            )
        if destination_station := self.request.query_params.get("destination"):
            queryset = queryset.filter(
                route__destination__name__icontains=destination_station
            )
        if source_station_departure_date := self.request.query_params.get(
            "departure-date"
        ):
            source_station_departure_date = datetime.strptime(
                source_station_departure_date, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                departure_time__date=source_station_departure_date
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JoureyDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source station name (ex. ?source=Lviv)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by destination station name "
                    "(ex. ?destination=Lviv)"
                ),
            ),
            OpenApiParameter(
                "departure-date",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by departure-date (ex. ?departure-date=2023-10-21)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Order.objects.prefetch_related("tickets")
        .order_by("-created_at")
        .annotate(total_tickets=Count("tickets"))
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)
