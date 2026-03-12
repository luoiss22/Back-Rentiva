from rest_framework.routers import DefaultRouter
from .views import (
    EspecialistaViewSet,
    ReporteMantenimientoViewSet,
    ResenaEspecialistaViewSet,
)

router = DefaultRouter()
router.register(r"especialistas", EspecialistaViewSet)
router.register(r"reportes-mantenimiento", ReporteMantenimientoViewSet, basename="reporte-mantenimiento")
router.register(r"resenas-especialistas", ResenaEspecialistaViewSet, basename="resena-especialista")

urlpatterns = router.urls
