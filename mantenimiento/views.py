from rest_framework import viewsets

from autenticacion.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
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
    filterset_fields = ("especialidad", "ciudad", "disponible")
    search_fields = ("nombre", "especialidad", "ciudad")
    ordering_fields = ("calificacion", "nombre")

    def get_serializer_class(self):
        if self.action == "list":
            return EspecialistaListSerializer
        return EspecialistaSerializer


class ReporteMantenimientoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado", "prioridad", "propiedad", "especialista", "propietario")
    search_fields = ("descripcion",)
    ordering_fields = ("created_at", "prioridad")

    def get_queryset(self):
        qs = ReporteMantenimiento.objects.select_related(
            "propiedad", "especialista", "propietario",
        ).prefetch_related("resenas")
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteMantenimientoListSerializer
        return ReporteMantenimientoSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "rol", None) != "admin":
            serializer.save(propietario=user)
        else:
            serializer.save()


class ResenaEspecialistaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = ResenaEspecialistaSerializer
    filterset_fields = ("especialista", "propietario", "calificacion")

    def get_queryset(self):
        qs = ResenaEspecialista.objects.select_related(
            "especialista", "propietario", "reporte",
        )
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(propietario=user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "rol", None) != "admin":
            serializer.save(propietario=user)
        else:
            serializer.save()
