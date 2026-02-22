from rest_framework import viewsets
from .models import Especialista, ReporteMantenimiento, ResenaEspecialista
from .serializers import (
    EspecialistaSerializer,
    EspecialistaListSerializer,
    ReporteMantenimientoSerializer,
    ReporteMantenimientoListSerializer,
    ResenaEspecialistaSerializer,
)


class EspecialistaViewSet(viewsets.ModelViewSet):
    queryset = Especialista.objects.all()
    filterset_fields = ("especialidad", "ciudad", "disponible")
    search_fields = ("nombre", "especialidad", "ciudad")
    ordering_fields = ("calificacion", "nombre")

    def get_serializer_class(self):
        if self.action == "list":
            return EspecialistaListSerializer
        return EspecialistaSerializer


class ReporteMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = ReporteMantenimiento.objects.select_related(
        "propiedad", "especialista", "propietario",
    ).prefetch_related("resenas")
    filterset_fields = ("estado", "prioridad", "propiedad", "especialista", "propietario")
    search_fields = ("descripcion",)
    ordering_fields = ("created_at", "prioridad")

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteMantenimientoListSerializer
        return ReporteMantenimientoSerializer


class ResenaEspecialistaViewSet(viewsets.ModelViewSet):
    queryset = ResenaEspecialista.objects.select_related(
        "especialista", "propietario", "reporte",
    )
    serializer_class = ResenaEspecialistaSerializer
    filterset_fields = ("especialista", "propietario", "calificacion")
