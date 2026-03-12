from rest_framework.routers import DefaultRouter
from .views import (
    PropiedadViewSet,
    PropiedadDetalleViewSet,
    MobiliarioViewSet,
    PropiedadMobiliarioViewSet,
    FotoPropiedadViewSet,
)

router = DefaultRouter()
router.register(r"propiedades", PropiedadViewSet, basename="propiedad")
router.register(r"propiedad-detalles", PropiedadDetalleViewSet, basename="propiedad-detalle")
router.register(r"mobiliario", MobiliarioViewSet)
router.register(r"propiedad-mobiliario", PropiedadMobiliarioViewSet, basename="propiedad-mobiliario")
router.register(r"fotos-propiedad", FotoPropiedadViewSet, basename="foto-propiedad")

urlpatterns = router.urls
