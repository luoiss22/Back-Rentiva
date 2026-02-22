from rest_framework import viewsets
from .models import Pago, FichaPago, Factura
from .serializers import (
    PagoSerializer,
    PagoListSerializer,
    FichaPagoSerializer,
    FacturaSerializer,
)


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.select_related("contrato").prefetch_related(
        "ficha", "factura",
    )
    filterset_fields = ("estado", "metodo_pago", "contrato")
    search_fields = ("periodo", "referencia")
    ordering_fields = ("fecha_limite", "fecha_pago", "monto")

    def get_serializer_class(self):
        if self.action == "list":
            return PagoListSerializer
        return PagoSerializer


class FichaPagoViewSet(viewsets.ModelViewSet):
    queryset = FichaPago.objects.select_related("pago")
    serializer_class = FichaPagoSerializer
    filterset_fields = ("pago",)


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.select_related(
        "pago", "datos_fiscales_emisor", "datos_fiscales_receptor",
    )
    serializer_class = FacturaSerializer
    filterset_fields = ("pago",)
    search_fields = ("folio_fiscal",)
