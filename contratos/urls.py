from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, HistorialContratoViewSet

router = DefaultRouter()
router.register(r"contratos", ContratoViewSet, basename="contrato")
router.register(r"historial-contratos", HistorialContratoViewSet, basename="historial-contrato")

urlpatterns = router.urls
