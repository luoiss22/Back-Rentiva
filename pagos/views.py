from rest_framework import viewsets

from autenticacion.models import Administrador
from autenticacion.permissions import IsOwnerOrAdmin
from .models import Pago, FichaPago, Factura
from .serializers import (
    PagoSerializer,
    PagoListSerializer,
    FichaPagoSerializer,
    FacturaSerializer,
)


from .utils import generar_pagos_pendientes

class PagoViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los pagos.
    Propietario: solo pagos de contratos de sus propiedades.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado", "metodo_pago", "contrato", "contrato__arrendatario", "contrato__propiedad")
    search_fields = ("periodo", "referencia")
    ordering_fields = ("fecha_limite", "fecha_pago", "monto")

    def list(self, request, *args, **kwargs):
        # Generar pagos pendientes automáticamente al listar
        # El try/except evita que un error en la generación rompa el listado
        try:
            generar_pagos_pendientes(request.user)
        except Exception:
            pass
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = Pago.objects.select_related(
            "contrato__propiedad__propietario",
            "contrato__arrendatario",
        ).prefetch_related("ficha", "factura")
        
        # Filtro manual de propiedad
        prop_id = self.request.query_params.get("propiedad")
        if prop_id:
            qs = qs.filter(contrato__propiedad_id=prop_id)
            
        user = self.request.user
        if isinstance(user, Administrador):
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
        if isinstance(user, Administrador):
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
        if isinstance(user, Administrador):
            return qs
        return qs.filter(pago__contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.pago.contrato.propiedad.propietario_id
