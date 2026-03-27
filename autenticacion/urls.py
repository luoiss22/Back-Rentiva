from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdministradorViewSet,
    PropietarioViewSet,
    registro_view,
    registro_admin_view,
    login_view,
    me_view,
    cambio_password_view,
    logout_view,
)

router = DefaultRouter()
router.register(r"administradores", AdministradorViewSet, basename="administrador")
router.register(r"propietarios", PropietarioViewSet, basename="propietario")

urlpatterns = [
    # Auth endpoints (publicos)
    path("auth/registro/", registro_view, name="auth-registro"),
    path("auth/login/", login_view, name="auth-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # Auth endpoints (protegidos)
    path("auth/me/", me_view, name="auth-me"),
    path("auth/cambio-password/", cambio_password_view, name="auth-cambio-password"),
    path("auth/logout/", logout_view, name="auth-logout"),
    # Admin only: registrar otro admin
    path("admin/registro/", registro_admin_view, name="admin-registro"),
] + router.urls
