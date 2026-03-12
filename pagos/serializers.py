from rest_framework import serializers
from .models import Pago, FichaPago, Factura


class FichaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichaPago
        fields = "__all__"
        read_only_fields = ("fecha_generacion",)

    def validate_pago(self, pago):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "rol", None) != "admin":
            if pago.contrato.propiedad.propietario_id != user.pk:
                raise serializers.ValidationError(
                    "No puedes crear fichas en pagos ajenos."
                )
        return pago


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = "__all__"

    def validate_pago(self, pago):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "rol", None) != "admin":
            if pago.contrato.propiedad.propietario_id != user.pk:
                raise serializers.ValidationError(
                    "No puedes crear facturas en pagos ajenos."
                )
        return pago


class PagoSerializer(serializers.ModelSerializer):
    ficha = FichaPagoSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)

    class Meta:
        model = Pago
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_contrato(self, contrato):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "rol", None) != "admin":
            if contrato.propiedad.propietario_id != user.pk:
                raise serializers.ValidationError(
                    "No puedes crear pagos en contratos ajenos."
                )
        return contrato


class PagoListSerializer(serializers.ModelSerializer):
    contrato_id = serializers.IntegerField(source="contrato.id", read_only=True)

    class Meta:
        model = Pago
        fields = (
            "id", "contrato_id", "periodo", "monto",
            "fecha_limite", "fecha_pago", "estado", "recargo_mora",
        )
