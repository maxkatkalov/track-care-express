from rest_framework.routers import DefaultRouter

from .views import (
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    TrainTypeViewSet
)

router = DefaultRouter()
router.register("stations", StationViewSet, basename="stations")
router.register("routes", RouteViewSet, basename="routes")
router.register("trains", TrainViewSet, basename="trains")
router.register("trains-type", TrainTypeViewSet, basename="trains-type")

urlpatterns = router.urls
