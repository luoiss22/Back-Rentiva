from rest_framework import serializers
from .models import Pago, FichaPago, Factura
from fiscal.models import DatosFiscales


def _calcular_datos_fiscales_faltantes(pago):
    """
    Devuelve una lista indicando quién no tiene DatosFiscales registrados.
    Posibles valores en la lista: "inquilino", "propietario"
    """
    import logging
    log = logging.getLogger(__name__)
    faltantes = []
    try:
        contrato = pago.contrato
        arrendatario_id = contrato.arrendatario_id
        propietario_id = contrato.propiedad.propietario_id

        tiene_inquilino = DatosFiscales.objects.filter(
            tipo_entidad="arrendatario", entidad_id=arrendatario_id
        ).exists()
        tiene_propietario = DatosFiscales.objects.filter(
            tipo_entidad="propietario", entidad_id=propietario_id
        ).exists()

        log.warning(
            "[FISCAL] pago=%s arrendatario_id=%s propietario_id=%s "
            "tiene_inquilino=%s tiene_propietario=%s",
            pago.pk, arrendatario_id, propietario_id,
            tiene_inquilino, tiene_propietario,
        )

        if not tiene_inquilino:
            faltantes.append("inquilino")
        if not tiene_propietario:
            faltantes.append("propietario")

    except Exception as e:
        log.warning(
            "[FISCAL] Error calculando datos_fiscales_faltantes para pago %s: %s",
            pago.pk, e
        )
        return ["inquilino", "propietario"]

    return faltantes


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
        read_only_fields = ("datos_fiscales_emisor", "datos_fiscales_receptor")

    def validate_pago(self, pago):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "rol", None) != "admin":
            if pago.contrato.propiedad.propietario_id != user.pk:
                raise serializers.ValidationError(
                    "No puedes crear facturas en pagos ajenos."
                )
        if hasattr(pago, "factura"):
            raise serializers.ValidationError(
                "Este pago ya tiene una factura generada."
            )
        return pago

    def create(self, validated_data):
        pago = validated_data["pago"]
        arrendatario_id = pago.contrato.arrendatario_id
        propietario_id = pago.contrato.propiedad.propietario_id

        emisor = DatosFiscales.objects.filter(
            tipo_entidad="propietario", entidad_id=propietario_id
        ).first()
        if not emisor:
            raise serializers.ValidationError(
                {"datos_fiscales_emisor": "El propietario no tiene datos fiscales registrados."}
            )

        receptor = DatosFiscales.objects.filter(
            tipo_entidad="arrendatario", entidad_id=arrendatario_id
        ).first()
        if not receptor:
            raise serializers.ValidationError(
                {"datos_fiscales_receptor": "El inquilino no tiene datos fiscales registrados."}
            )

        validated_data["datos_fiscales_emisor"] = emisor
        validated_data["datos_fiscales_receptor"] = receptor
        return super().create(validated_data)


class PagoSerializer(serializers.ModelSerializer):
    ficha = FichaPagoSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)
    inquilino_nombre = serializers.SerializerMethodField()
    datos_fiscales_faltantes = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_datos_fiscales_faltantes(self, obj):
        return _calcular_datos_fiscales_faltantes(obj)

    def get_inquilino_nombre(self, obj):
        try:
            return f"{obj.contrato.arrendatario.nombre} {obj.contrato.arrendatario.apellidos}".strip()
        except AttributeError:
            return "Desconocido"

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
    propiedad_id = serializers.IntegerField(source="contrato.propiedad.id", read_only=True)
    inquilino_nombre = serializers.SerializerMethodField()
    ficha = FichaPagoSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)
    datos_fiscales_faltantes = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = (
            "id", "contrato_id", "propiedad_id", "inquilino_nombre", "periodo", "monto",
            "fecha_limite", "fecha_pago", "estado", "recargo_mora",
            "metodo_pago", "referencia", "comprobante_url", "created_at",
            "ficha", "factura", "datos_fiscales_faltantes"
        )

    def get_inquilino_nombre(self, obj):
        try:
            return f"{obj.contrato.arrendatario.nombre} {obj.contrato.arrendatario.apellidos}".strip()
        except AttributeError:
            return "Desconocido"

    def get_datos_fiscales_faltantes(self, obj):
        return _calcular_datos_fiscales_faltantes(obj)
