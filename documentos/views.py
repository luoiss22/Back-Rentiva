from rest_framework import viewsets

from autenticacion.models import Administrador
from autenticacion.permissions import IsOwnerOrAdmin
from .models import Documento
from .serializers import DocumentoSerializer, DocumentoListSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los documentos.
    Propietario: solo ve documentos vinculados a sus entidades.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("tipo_entidad", "entidad_id", "tipo_documento")
    search_fields = ("nombre_archivo", "descripcion")

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentoListSerializer
        return DocumentoSerializer

    def get_queryset(self):
        qs = Documento.objects.all()
        user = self.request.user
        if isinstance(user, Administrador):
            return qs
        # Filtra documentos cuyo tipo_entidad=propietario y entidad_id=user.pk
        # más los vinculados a propiedades, contratos, etc. del propietario
        from django.db.models import Q
        from propiedades.models import Propiedad
        from contratos.models import Contrato
        from arrendatarios.models import Arrendatario

        propiedad_ids = Propiedad.objects.filter(
            propietario=user,
        ).values_list("id", flat=True)
        contrato_ids = Contrato.objects.filter(
            propiedad__propietario=user,
        ).values_list("id", flat=True)
        arrendatario_ids = Arrendatario.objects.filter(
            propietario=user,
        ).values_list("id", flat=True)

        return qs.filter(
            Q(tipo_entidad="propietario", entidad_id=user.pk)
            | Q(tipo_entidad="propiedad", entidad_id__in=propiedad_ids)
            | Q(tipo_entidad="contrato", entidad_id__in=contrato_ids)
            | Q(tipo_entidad="arrendatario", entidad_id__in=arrendatario_ids)
        )

    def get_owner_id(self, obj):
        if obj.tipo_entidad == "propietario":
            return obj.entidad_id
        if obj.tipo_entidad == "propiedad":
            from propiedades.models import Propiedad
            return Propiedad.objects.filter(pk=obj.entidad_id).values_list("propietario_id", flat=True).first()
        if obj.tipo_entidad == "contrato":
            from contratos.models import Contrato
            return Contrato.objects.filter(pk=obj.entidad_id).values_list("propiedad__propietario_id", flat=True).first()
        if obj.tipo_entidad == "arrendatario":
            from arrendatarios.models import Arrendatario
            return Arrendatario.objects.filter(pk=obj.entidad_id).values_list("propietario_id", flat=True).first()
        return None
