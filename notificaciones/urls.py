from rest_framework.routers import DefaultRouter
from .views import NotificacionViewSet, NotificacionLogViewSet

router = DefaultRouter()
router.register(r"notificaciones", NotificacionViewSet, basename="notificacion")
router.register(r"notificacion-logs", NotificacionLogViewSet, basename="notificacion-log")

urlpatterns = router.urls
