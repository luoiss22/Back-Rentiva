from rest_framework import serializers
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
