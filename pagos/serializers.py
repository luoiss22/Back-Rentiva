from rest_framework import serializers
from .models import Pago, FichaPago, Factura


class FichaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichaPago
        fields = "__all__"
        read_only_fields = ("fecha_generacion",)


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = "__all__"


class PagoSerializer(serializers.ModelSerializer):
    ficha = FichaPagoSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)

    class Meta:
        model = Pago
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class PagoListSerializer(serializers.ModelSerializer):
    contrato_id = serializers.IntegerField(source="contrato.id", read_only=True)

    class Meta:
        model = Pago
        fields = (
            "id", "contrato_id", "periodo", "monto",
            "fecha_limite", "fecha_pago", "estado", "recargo_mora",
        )
