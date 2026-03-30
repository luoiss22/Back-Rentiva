from rest_framework import serializers
from autenticacion.models import Administrador
from .models import Contrato, HistorialContrato


class HistorialContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialContrato
        fields = "__all__"
        read_only_fields = ("fecha_cambio", "created_at")


class ContratoSerializer(serializers.ModelSerializer):
    historial = HistorialContratoSerializer(many=True, read_only=True)
    propiedad_nombre = serializers.CharField(
        source="propiedad.nombre", read_only=True,
    )
    arrendatario_nombre = serializers.CharField(
        source="arrendatario.__str__", read_only=True,
    )

    class Meta:
        model = Contrato
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        is_admin = isinstance(user, Administrador)

        # Validar que la propiedad pertenece al usuario
        propiedad = attrs.get("propiedad", getattr(self.instance, "propiedad", None))
        if propiedad and not is_admin and propiedad.propietario_id != user.pk:
            raise serializers.ValidationError(
                {"propiedad": "No puedes crear contratos en propiedades ajenas."}
            )

        # Validar que el arrendatario pertenece al usuario
        arrendatario = attrs.get("arrendatario", getattr(self.instance, "arrendatario", None))
        if arrendatario and not is_admin and arrendatario.propietario_id != user.pk:
            raise serializers.ValidationError(
                {"arrendatario": "No puedes usar arrendatarios ajenos."}
            )

        # Ejecutar validaciones del modelo
        instance = Contrato(**attrs)
        if self.instance:
            instance.pk = self.instance.pk
        instance.clean()
        return attrs


class ContratoListSerializer(serializers.ModelSerializer):
    propiedad_nombre = serializers.CharField(
        source="propiedad.nombre", read_only=True,
    )
    arrendatario_nombre = serializers.CharField(
        source="arrendatario.__str__", read_only=True,
    )

    class Meta:
        model = Contrato
        fields = (
            "id", "propiedad", "propiedad_nombre",
            "arrendatario", "arrendatario_nombre",
            "fecha_inicio", "fecha_fin", "renta_acordada",
            "periodo_pago", "estado",
        )
