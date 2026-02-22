from rest_framework.routers import DefaultRouter
from .views import NotificacionViewSet, NotificacionLogViewSet

router = DefaultRouter()
router.register(r"notificaciones", NotificacionViewSet)
router.register(r"notificacion-logs", NotificacionLogViewSet)

urlpatterns = router.urls
