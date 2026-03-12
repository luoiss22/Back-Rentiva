from rest_framework import viewsets

from autenticacion.permissions import IsOwnerOrAdmin
from .models import Notificacion, NotificacionLog
from .serializers import (
    NotificacionSerializer,
    NotificacionListSerializer,
    NotificacionLogSerializer,
)


class NotificacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("tipo", "medio", "contrato")
    search_fields = ("titulo", "mensaje")
    ordering_fields = ("fecha_programada",)

    def get_queryset(self):
        qs = Notificacion.objects.select_related(
            "contrato__propiedad__propietario",
        ).prefetch_related("logs")
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(contrato__propiedad__propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return NotificacionListSerializer
        return NotificacionSerializer

    def get_owner_id(self, obj):
        return obj.contrato.propiedad.propietario_id


class NotificacionLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = NotificacionLogSerializer
    filterset_fields = ("notificacion", "estado")
    http_method_names = ["get", "head", "options"]  # Solo lectura

    def get_queryset(self):
        qs = NotificacionLog.objects.select_related(
            "notificacion__contrato__propiedad__propietario",
        )
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(notificacion__contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.notificacion.contrato.propiedad.propietario_id
