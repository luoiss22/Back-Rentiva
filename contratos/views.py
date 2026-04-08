from django.utils import timezone
from rest_framework import viewsets

from autenticacion.models import Administrador
from autenticacion.permissions import IsOwnerOrAdmin
from .models import Contrato, HistorialContrato
from .serializers import (
    ContratoSerializer,
    ContratoListSerializer,
    HistorialContratoSerializer,
)


def _sync_propiedad_estado(contrato):
    """Sincroniza el estado de la propiedad según el estado del contrato."""
    from propiedades.models import Propiedad
    propiedad = contrato.propiedad
    if contrato.estado == Contrato.Estado.ACTIVO:
        nuevo = Propiedad.Estado.RENTADA
    elif contrato.estado in (Contrato.Estado.FINALIZADO, Contrato.Estado.CANCELADO):
        # Solo libera si no hay otro contrato activo en la misma propiedad
        tiene_otro_activo = Contrato.objects.filter(
            propiedad=propiedad,
            estado=Contrato.Estado.ACTIVO,
        ).exclude(pk=contrato.pk).exists()
        nuevo = Propiedad.Estado.DISPONIBLE if not tiene_otro_activo else None
    else:
        nuevo = None

    if nuevo and propiedad.estado != nuevo:
        propiedad.estado = nuevo
        propiedad.save(update_fields=['estado'])


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
        if isinstance(user, Administrador):
            return qs
        return qs.filter(propiedad__propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ContratoListSerializer
        return ContratoSerializer

    def perform_create(self, serializer):
        contrato = serializer.save()
        # Si el contrato se crea ya en estado activo, sincronizar propiedad y arrendatario.
        if contrato.estado == Contrato.Estado.ACTIVO:
            _sync_propiedad_estado(contrato)
            from arrendatarios.models import Arrendatario
            Arrendatario.objects.filter(pk=contrato.arrendatario_id).update(estado='activo')

    def perform_update(self, serializer):
        instance = self.get_object()
        estado_anterior = instance.estado
        contrato = serializer.save()
        estado_nuevo = contrato.estado

        # Registrar en historial si el estado cambió
        if estado_anterior != estado_nuevo:
            HistorialContrato.objects.create(
                contrato=contrato,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
            )
            _sync_propiedad_estado(contrato)

            # Al activar, asegurarse de que el arrendatario esté activo
            if estado_nuevo == Contrato.Estado.ACTIVO:
                from arrendatarios.models import Arrendatario
                Arrendatario.objects.filter(pk=contrato.arrendatario_id).update(estado='activo')

            # Al cancelar o finalizar, marcar los pagos pendientes/vencidos como cancelados
            if estado_nuevo in (Contrato.Estado.CANCELADO, Contrato.Estado.FINALIZADO):
                from pagos.models import Pago
                Pago.objects.filter(
                    contrato=contrato,
                    estado__in=(Pago.Estado.PENDIENTE, Pago.Estado.VENCIDO),
                ).update(estado=Pago.Estado.CANCELADO)

                # Si el arrendatario ya no tiene ningún contrato activo, marcarlo inactivo
                from arrendatarios.models import Arrendatario
                arrendatario = contrato.arrendatario
                tiene_activos = Contrato.objects.filter(
                    arrendatario=arrendatario,
                    estado=Contrato.Estado.ACTIVO,
                ).exists()
                if not tiene_activos:
                    Arrendatario.objects.filter(pk=arrendatario.pk).update(estado='inactivo')

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
        if isinstance(user, Administrador):
            return qs
        return qs.filter(contrato__propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.contrato.propiedad.propietario_id
