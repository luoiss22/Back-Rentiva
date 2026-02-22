"""Rentiva Backend — Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include("autenticacion.urls")),
    path("api/v1/", include("arrendatarios.urls")),
    path("api/v1/", include("propiedades.urls")),
    path("api/v1/", include("contratos.urls")),
    path("api/v1/", include("pagos.urls")),
    path("api/v1/", include("notificaciones.urls")),
    path("api/v1/", include("mantenimiento.urls")),
    path("api/v1/", include("documentos.urls")),
    path("api/v1/", include("fiscal.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
