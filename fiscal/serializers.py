from rest_framework import serializers
from .models import DatosFiscales


class DatosFiscalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosFiscales
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if not user or getattr(user, "rol", None) == "admin":
            return attrs

        tipo = attrs.get("tipo_entidad", getattr(self.instance, "tipo_entidad", None))
        eid = attrs.get("entidad_id", getattr(self.instance, "entidad_id", None))

        if tipo == "propietario" and eid != user.pk:
            raise serializers.ValidationError(
                {"entidad_id": "No puedes crear datos fiscales de otro propietario."}
            )
        if tipo == "arrendatario":
            from arrendatarios.models import Arrendatario
            if not Arrendatario.objects.filter(pk=eid, propietario=user).exists():
                raise serializers.ValidationError(
                    {"entidad_id": "Arrendatario no encontrado o no te pertenece."}
                )
        return attrs


class DatosFiscalesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosFiscales
        fields = (
            "id", "tipo_entidad", "entidad_id",
            "nombre_o_razon_social", "rfc",
            "regimen_fiscal", "uso_cfdi",
            "codigo_postal", "correo_facturacion",
        )
