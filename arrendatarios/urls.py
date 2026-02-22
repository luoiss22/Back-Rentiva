from rest_framework.routers import DefaultRouter
from .views import ArrendatarioViewSet

router = DefaultRouter()
router.register(r"arrendatarios", ArrendatarioViewSet)

urlpatterns = router.urls
