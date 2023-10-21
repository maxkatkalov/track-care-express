from rest_framework.routers import DefaultRouter

from .views import StationViewSet, RouteViewSet

router = DefaultRouter()
router.register("stations", StationViewSet, basename="stations")
router.register("routes", RouteViewSet, basename="routes")

urlpatterns = router.urls
