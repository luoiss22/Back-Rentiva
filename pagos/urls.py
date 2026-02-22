from rest_framework.routers import DefaultRouter
from .views import PagoViewSet, FichaPagoViewSet, FacturaViewSet

router = DefaultRouter()
router.register(r"pagos", PagoViewSet)
router.register(r"fichas-pago", FichaPagoViewSet)
router.register(r"facturas", FacturaViewSet)

urlpatterns = router.urls
