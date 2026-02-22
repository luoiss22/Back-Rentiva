from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, HistorialContratoViewSet

router = DefaultRouter()
router.register(r"contratos", ContratoViewSet)
router.register(r"historial-contratos", HistorialContratoViewSet)

urlpatterns = router.urls
