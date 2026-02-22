from rest_framework.routers import DefaultRouter
from .views import (
    PropiedadViewSet,
    PropiedadDetalleViewSet,
    MobiliarioViewSet,
    PropiedadMobiliarioViewSet,
)

router = DefaultRouter()
router.register(r"propiedades", PropiedadViewSet)
router.register(r"propiedad-detalles", PropiedadDetalleViewSet)
router.register(r"mobiliario", MobiliarioViewSet)
router.register(r"propiedad-mobiliario", PropiedadMobiliarioViewSet)

urlpatterns = router.urls
