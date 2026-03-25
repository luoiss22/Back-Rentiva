from rest_framework import viewsets

from autenticacion.permissions import IsOwnerOrAdmin
from .models import DatosFiscales
from .serializers import DatosFiscalesSerializer, DatosFiscalesListSerializer


class DatosFiscalesViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los datos fiscales.
    Propietario: solo ve los suyos (tipo_entidad=propietario, entidad_id=user.pk)
    y los de sus arrendatarios.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("tipo_entidad", "entidad_id")
    search_fields = ("rfc", "nombre_o_razon_social")

    def get_serializer_class(self):
        if self.action == "list":
            return DatosFiscalesListSerializer
        return DatosFiscalesSerializer

    def get_owner_id(self, obj):
        """Para DatosFiscales de tipo propietario, el owner es entidad_id."""
        if obj.tipo_entidad == "propietario":
            return obj.entidad_id
        # Para arrendatario, buscar el propietario del arrendatario
        from arrendatarios.models import Arrendatario
        try:
            return Arrendatario.objects.filter(pk=obj.entidad_id).values_list("propietario_id", flat=True).first()
        except Exception:
            return None

    def get_queryset(self):
        qs = DatosFiscales.objects.all()
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        from django.db.models import Q
        from arrendatarios.models import Arrendatario

        arrendatario_ids = Arrendatario.objects.filter(
            propietario=user,
        ).values_list("id", flat=True)

        return qs.filter(
            Q(tipo_entidad="propietario", entidad_id=user.pk)
            | Q(tipo_entidad="arrendatario", entidad_id__in=arrendatario_ids)
        )
