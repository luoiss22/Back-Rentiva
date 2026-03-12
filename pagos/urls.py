from rest_framework.routers import DefaultRouter
from .views import PagoViewSet, FichaPagoViewSet, FacturaViewSet

router = DefaultRouter()
router.register(r"pagos", PagoViewSet, basename="pago")
router.register(r"fichas-pago", FichaPagoViewSet, basename="ficha-pago")
router.register(r"facturas", FacturaViewSet, basename="factura")

urlpatterns = router.urls
