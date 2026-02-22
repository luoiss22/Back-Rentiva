from rest_framework.routers import DefaultRouter
from .views import DatosFiscalesViewSet

router = DefaultRouter()
router.register(r"datos-fiscales", DatosFiscalesViewSet)

urlpatterns = router.urls
