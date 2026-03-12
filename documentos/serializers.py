from rest_framework import serializers
from .models import Documento


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = "__all__"
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if not user or getattr(user, "rol", None) == "admin":
            return attrs

        tipo = attrs.get("tipo_entidad", getattr(self.instance, "tipo_entidad", None))
        eid = attrs.get("entidad_id", getattr(self.instance, "entidad_id", None))

        if tipo == "propietario" and eid != user.pk:
            raise serializers.ValidationError(
                {"entidad_id": "No puedes adjuntar documentos a otro propietario."}
            )
        if tipo == "propiedad":
            from propiedades.models import Propiedad
            if not Propiedad.objects.filter(pk=eid, propietario=user).exists():
                raise serializers.ValidationError(
                    {"entidad_id": "Propiedad no encontrada o no te pertenece."}
                )
        if tipo == "arrendatario":
            from arrendatarios.models import Arrendatario
            if not Arrendatario.objects.filter(pk=eid, propietario=user).exists():
                raise serializers.ValidationError(
                    {"entidad_id": "Arrendatario no encontrado o no te pertenece."}
                )
        if tipo == "contrato":
            from contratos.models import Contrato
            if not Contrato.objects.filter(pk=eid, propiedad__propietario=user).exists():
                raise serializers.ValidationError(
                    {"entidad_id": "Contrato no encontrado o no te pertenece."}
                )
        if tipo == "reporte":
            from mantenimiento.models import ReporteMantenimiento
            if not ReporteMantenimiento.objects.filter(pk=eid, propietario=user).exists():
                raise serializers.ValidationError(
                    {"entidad_id": "Reporte no encontrado o no te pertenece."}
                )
        return attrs


class DocumentoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ("id", "tipo_entidad", "entidad_id", "tipo_documento", "nombre_archivo", "created_at")
