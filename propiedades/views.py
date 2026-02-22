from rest_framework import viewsets
from .models import Propiedad, PropiedadDetalle, Mobiliario, PropiedadMobiliario
from .serializers import (
    PropiedadSerializer,
    PropiedadListSerializer,
    PropiedadDetalleSerializer,
    MobiliarioSerializer,
    PropiedadMobiliarioSerializer,
)


class PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.select_related("propietario").prefetch_related(
        "detalles", "mobiliarios__mobiliario",
    )
    filterset_fields = ("estado", "tipo", "propietario", "ciudad")
    search_fields = ("nombre", "direccion", "ciudad")
    ordering_fields = ("nombre", "costo_renta", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PropiedadListSerializer
        return PropiedadSerializer


class PropiedadDetalleViewSet(viewsets.ModelViewSet):
    queryset = PropiedadDetalle.objects.all()
    serializer_class = PropiedadDetalleSerializer
    filterset_fields = ("propiedad",)


class MobiliarioViewSet(viewsets.ModelViewSet):
    queryset = Mobiliario.objects.all()
    serializer_class = MobiliarioSerializer
    search_fields = ("nombre", "tipo")


class PropiedadMobiliarioViewSet(viewsets.ModelViewSet):
    queryset = PropiedadMobiliario.objects.select_related(
        "propiedad", "mobiliario",
    )
    serializer_class = PropiedadMobiliarioSerializer
    filterset_fields = ("propiedad", "mobiliario", "estado")
