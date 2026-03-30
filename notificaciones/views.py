from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from autenticacion.models import Administrador
from autenticacion.permissions import IsOwnerOrAdmin
from .models import Notificacion, NotificacionLog
from .serializers import (
    NotificacionSerializer,
    NotificacionListSerializer,
    NotificacionLogSerializer,
)
from .utils import generar_notificaciones_automaticas


class NotificacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("tipo", "medio", "contrato", "leida")
    search_fields = ("titulo", "mensaje")
    ordering_fields = ("fecha_programada",)

    def list(self, request, *args, **kwargs):
        # Generar notificaciones automáticas al listar
        try:
            generar_notificaciones_automaticas(request.user)
        except Exception:
            pass  # Si falla la generación automática no interrumpimos el listado
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = Notificacion.objects.select_related(
            "contrato__propiedad__propietario",
        ).prefetch_related("logs")
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        return qs.filter(contrato__propiedad__propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return NotificacionListSerializer
        return NotificacionSerializer

    def get_owner_id(self, obj):
        return obj.contrato.propiedad.propietario_id

    @action(detail=False, methods=["post"])
    def marcar_leidas(self, request):
        """Marca todas las notificaciones del usuario como leídas."""
        qs = self.get_queryset().filter(leida=False)
        actualizadas = qs.update(leida=True)
        return Response({"leidas": actualizadas, "status": "ok"}, status=status.HTTP_200_OK)


class NotificacionLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = NotificacionLogSerializer
    filterset_fields = ("notificacion", "estado")
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        qs = NotificacionLog.objects.select_related(
            "notificacion__contrato__propiedad__propietario",
        )
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        return qs.filter(notificacion__contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.notificacion.contrato.propiedad.propietario_id
