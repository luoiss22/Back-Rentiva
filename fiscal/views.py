from rest_framework import viewsets

from autenticacion.models import Administrador
from autenticacion.permissions import IsOwnerOrAdmin
from arrendatarios.models import Arrendatario
from .models import DatosFiscales
from .serializers import DatosFiscalesSerializer, DatosFiscalesListSerializer


class DatosFiscalesViewSet(viewsets.ModelViewSet):
    """
    Propietario: ve los suyos (tipo_entidad=propietario, entidad_id=user.pk)
    y los de sus arrendatarios.
    Admin: NO tiene acceso a datos fiscales de los usuarios.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("tipo_entidad", "entidad_id")
    search_fields = ("rfc", "nombre_o_razon_social")

    def get_serializer_class(self):
        if self.action == "list":
            return DatosFiscalesListSerializer
        return DatosFiscalesSerializer

    def get_owner_id(self, obj):
        if obj.tipo_entidad == "propietario":
            return obj.entidad_id
        try:
            return Arrendatario.objects.filter(pk=obj.entidad_id).values_list("propietario_id", flat=True).first()
        except Exception:
            return None

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, Administrador):
            return DatosFiscales.objects.none()
        from django.db.models import Q
        arrendatario_ids = Arrendatario.objects.filter(propietario=user).values_list("id", flat=True)

        return DatosFiscales.objects.filter(
            Q(tipo_entidad="propietario", entidad_id=user.pk)
            | Q(tipo_entidad="arrendatario", entidad_id__in=arrendatario_ids)
        )
