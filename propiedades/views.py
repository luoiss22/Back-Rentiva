from rest_framework import viewsets

from autenticacion.models import Administrador
from autenticacion.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
from .models import Propiedad, PropiedadDetalle, Mobiliario, PropiedadMobiliario, FotoPropiedad
from .serializers import (
    PropiedadSerializer,
    PropiedadListSerializer,
    PropiedadDetalleSerializer,
    MobiliarioSerializer,
    PropiedadMobiliarioSerializer,
    FotoPropiedadSerializer,
)


class PropiedadViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todas las propiedades.
    Propietario: solo ve sus propiedades.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado", "tipo", "propietario", "ciudad")
    search_fields = ("nombre", "direccion", "ciudad")
    ordering_fields = ("nombre", "costo_renta", "created_at")

    def get_queryset(self):
        qs = Propiedad.objects.select_related("propietario").prefetch_related(
            "detalles", "mobiliarios__mobiliario", "fotos",
        )
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        return qs.filter(propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return PropiedadListSerializer
        return PropiedadSerializer

    def perform_create(self, serializer):
        """Si no es admin, fuerza el propietario al usuario autenticado."""
        user = self.request.user
        if not isinstance(user, Administrador):
            serializer.save(propietario=user)
        else:
            serializer.save()


class PropiedadDetalleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = PropiedadDetalleSerializer
    filterset_fields = ("propiedad",)

    def get_queryset(self):
        qs = PropiedadDetalle.objects.select_related("propiedad__propietario")
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        return qs.filter(propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.propiedad.propietario_id


class MobiliarioViewSet(viewsets.ModelViewSet):
    """Catálogo compartido. Admin escribe, propietario solo lee."""
    queryset = Mobiliario.objects.all()
    serializer_class = MobiliarioSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("nombre", "tipo")


class PropiedadMobiliarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = PropiedadMobiliarioSerializer
    filterset_fields = ("propiedad", "mobiliario", "estado")

    def get_queryset(self):
        qs = PropiedadMobiliario.objects.select_related(
            "propiedad__propietario", "mobiliario",
        )
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        return qs.filter(propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.propiedad.propietario_id


class FotoPropiedadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FotoPropiedadSerializer
    filterset_fields = ("propiedad", "es_principal")
    ordering_fields = ("orden", "created_at")

    def get_queryset(self):
        qs = FotoPropiedad.objects.select_related("propiedad__propietario")
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        return qs.filter(propiedad__propietario=user)

    def get_owner_id(self, obj):
        return obj.propiedad.propietario_id
