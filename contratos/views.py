from rest_framework import viewsets

from autenticacion.permissions import IsOwnerOrAdmin
from .models import Contrato, HistorialContrato
from .serializers import (
    ContratoSerializer,
    ContratoListSerializer,
    HistorialContratoSerializer,
)


class ContratoViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los contratos.
    Propietario: solo ve contratos de sus propiedades.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado", "periodo_pago", "propiedad", "arrendatario")
    search_fields = ("propiedad__nombre", "arrendatario__nombre", "observaciones")
    ordering_fields = ("fecha_inicio", "fecha_fin", "renta_acordada")

    def get_queryset(self):
        qs = Contrato.objects.select_related(
            "propiedad__propietario", "arrendatario",
        ).prefetch_related("historial")
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(propiedad__propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ContratoListSerializer
        return ContratoSerializer

    def get_owner_id(self, obj):
        return obj.propiedad.propietario_id


class HistorialContratoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = HistorialContratoSerializer
    filterset_fields = ("contrato",)
    http_method_names = ["get", "head", "options"]  # Solo lectura

    def get_queryset(self):
        qs = HistorialContrato.objects.select_related(
            "contrato__propiedad__propietario",
        )
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.contrato.propiedad.propietario_id
