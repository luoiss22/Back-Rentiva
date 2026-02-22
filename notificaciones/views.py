from rest_framework import viewsets
from .models import Notificacion, NotificacionLog
from .serializers import (
    NotificacionSerializer,
    NotificacionListSerializer,
    NotificacionLogSerializer,
)


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.select_related("contrato").prefetch_related("logs")
    filterset_fields = ("tipo", "medio", "contrato")
    search_fields = ("titulo", "mensaje")
    ordering_fields = ("fecha_programada",)

    def get_serializer_class(self):
        if self.action == "list":
            return NotificacionListSerializer
        return NotificacionSerializer


class NotificacionLogViewSet(viewsets.ModelViewSet):
    queryset = NotificacionLog.objects.select_related("notificacion")
    serializer_class = NotificacionLogSerializer
    filterset_fields = ("notificacion", "estado")
