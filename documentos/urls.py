from rest_framework.routers import DefaultRouter
from .views import DocumentoViewSet

router = DefaultRouter()
router.register(r"documentos", DocumentoViewSet)

urlpatterns = router.urls
