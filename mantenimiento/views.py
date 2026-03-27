from django.utils import timezone
from rest_framework import viewsets

from autenticacion.permissions import IsAdminOrReadOnly, IsOwner
from .models import Especialista, ReporteMantenimiento, ResenaEspecialista
from .serializers import (
    EspecialistaSerializer,
    EspecialistaListSerializer,
    ReporteMantenimientoSerializer,
    ReporteMantenimientoListSerializer,
    ResenaEspecialistaSerializer,
)


class EspecialistaViewSet(viewsets.ModelViewSet):
    """Catálogo compartido. Admin escribe, propietario solo lee."""
    queryset = Especialista.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    # Quitamos especialidad de filterset_fields para que no sea match exacto.
    # El front usa ?search=Fontanero y el backend busca en nombre, especialidad y ciudad.
    filterset_fields = ("ciudad", "disponible")
    search_fields = ("nombre", "especialidad", "ciudad")
    ordering_fields = ("calificacion", "nombre")

    def get_serializer_class(self):
        if self.action == "list":
            return EspecialistaListSerializer
        return EspecialistaSerializer


class ReporteMantenimientoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    filterset_fields = ("estado", "prioridad", "propiedad", "especialista")
    search_fields = ("descripcion",)
    ordering_fields = ("created_at", "prioridad")

    def get_queryset(self):
        return ReporteMantenimiento.objects.select_related(
            "propiedad", "especialista", "propietario",
        ).prefetch_related("resenas").filter(propietario=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteMantenimientoListSerializer
        return ReporteMantenimientoSerializer

    def perform_create(self, serializer):
        serializer.save(propietario=self.request.user)

    def perform_update(self, serializer):
        """Si el estado cambia a 'resuelto', registra la fecha automáticamente."""
        instance = self.get_object()
        estado_anterior = instance.estado
        estado_nuevo = serializer.validated_data.get("estado", estado_anterior)

        extra = {}
        if estado_nuevo == ReporteMantenimiento.Estado.RESUELTO and estado_anterior != ReporteMantenimiento.Estado.RESUELTO:
            extra["fecha_resolucion"] = timezone.now()
        # Si lo sacan de resuelto, limpiamos la fecha
        elif estado_nuevo != ReporteMantenimiento.Estado.RESUELTO and estado_anterior == ReporteMantenimiento.Estado.RESUELTO:
            extra["fecha_resolucion"] = None

        serializer.save(**extra)

    def get_owner_id(self, obj):
        return obj.propietario_id


class ResenaEspecialistaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    serializer_class = ResenaEspecialistaSerializer
    filterset_fields = ("especialista", "calificacion")

    def get_queryset(self):
        return ResenaEspecialista.objects.select_related(
            "especialista", "propietario", "reporte",
        ).filter(propietario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(propietario=self.request.user)

    def get_owner_id(self, obj):
        return obj.propietario_id
