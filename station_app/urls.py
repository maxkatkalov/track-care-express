from rest_framework.routers import DefaultRouter

from .views import (
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    TrainTypeViewSet,
    CrewViewSet,
    JourneyViewSet,
)

router = DefaultRouter()
router.register("stations", StationViewSet, basename="stations")
router.register("routes", RouteViewSet, basename="routes")
router.register("trains", TrainViewSet, basename="trains")
router.register("trains-type", TrainTypeViewSet, basename="trains-type")
router.register("crew", CrewViewSet, basename="crew")
router.register("journeys", JourneyViewSet, basename="journeys")

urlpatterns = router.urls
