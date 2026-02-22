from rest_framework.routers import DefaultRouter
from .views import (
    EspecialistaViewSet,
    ReporteMantenimientoViewSet,
    ResenaEspecialistaViewSet,
)

router = DefaultRouter()
router.register(r"especialistas", EspecialistaViewSet)
router.register(r"reportes-mantenimiento", ReporteMantenimientoViewSet)
router.register(r"resenas-especialistas", ResenaEspecialistaViewSet)

urlpatterns = router.urls
