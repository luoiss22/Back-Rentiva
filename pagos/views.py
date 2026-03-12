from rest_framework import viewsets

from autenticacion.permissions import IsOwnerOrAdmin
from .models import Pago, FichaPago, Factura
from .serializers import (
    PagoSerializer,
    PagoListSerializer,
    FichaPagoSerializer,
    FacturaSerializer,
)


class PagoViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los pagos.
    Propietario: solo pagos de contratos de sus propiedades.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado", "metodo_pago", "contrato")
    search_fields = ("periodo", "referencia")
    ordering_fields = ("fecha_limite", "fecha_pago", "monto")

    def get_queryset(self):
        qs = Pago.objects.select_related(
            "contrato__propiedad__propietario",
        ).prefetch_related("ficha", "factura")
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(contrato__propiedad__propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return PagoListSerializer
        return PagoSerializer

    def get_owner_id(self, obj):
        return obj.contrato.propiedad.propietario_id


class FichaPagoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FichaPagoSerializer
    filterset_fields = ("pago",)

    def get_queryset(self):
        qs = FichaPago.objects.select_related(
            "pago__contrato__propiedad__propietario",
        )
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(pago__contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.pago.contrato.propiedad.propietario_id


class FacturaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FacturaSerializer
    filterset_fields = ("pago",)
    search_fields = ("folio_fiscal",)

    def get_queryset(self):
        qs = Factura.objects.select_related(
            "pago__contrato__propiedad__propietario",
            "datos_fiscales_emisor",
            "datos_fiscales_receptor",
        )
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(pago__contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.pago.contrato.propiedad.propietario_id
