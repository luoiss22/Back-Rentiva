from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PropietarioViewSet,
    registro_view,
    login_view,
    me_view,
    cambio_password_view,
    cambiar_rol_view,
    logout_view,
)

router = DefaultRouter()
router.register(r"propietarios", PropietarioViewSet, basename="propietario")

urlpatterns = [
    # Auth endpoints (públicos)
    path("auth/registro/", registro_view, name="auth-registro"),
    path("auth/login/", login_view, name="auth-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # Auth endpoints (protegidos — requieren Bearer token)
    path("auth/me/", me_view, name="auth-me"),
    path("auth/cambio-password/", cambio_password_view, name="auth-cambio-password"),
    path("auth/logout/", logout_view, name="auth-logout"),
    # Admin only
    path("admin/propietarios/<int:pk>/rol/", cambiar_rol_view, name="admin-cambiar-rol"),
] + router.urls
