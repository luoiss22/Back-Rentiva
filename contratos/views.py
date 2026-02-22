from rest_framework import viewsets
from .models import Contrato, HistorialContrato
from .serializers import (
    ContratoSerializer,
    ContratoListSerializer,
    HistorialContratoSerializer,
)


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.select_related(
        "propiedad", "arrendatario",
    ).prefetch_related("historial")
    filterset_fields = ("estado", "periodo_pago", "propiedad", "arrendatario")
    search_fields = ("propiedad__nombre", "arrendatario__nombre", "observaciones")
    ordering_fields = ("fecha_inicio", "fecha_fin", "renta_acordada")

    def get_serializer_class(self):
        if self.action == "list":
            return ContratoListSerializer
        return ContratoSerializer


class HistorialContratoViewSet(viewsets.ModelViewSet):
    queryset = HistorialContrato.objects.select_related("contrato")
    serializer_class = HistorialContratoSerializer
    filterset_fields = ("contrato",)
    http_method_names = ["get", "head", "options"]  # Solo lectura
