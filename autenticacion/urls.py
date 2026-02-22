from rest_framework.routers import DefaultRouter
from .views import PropietarioViewSet, CredencialViewSet

router = DefaultRouter()
router.register(r"propietarios", PropietarioViewSet)
router.register(r"credenciales", CredencialViewSet)

urlpatterns = router.urls
