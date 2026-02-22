from rest_framework import serializers
from .models import Propiedad, PropiedadDetalle, Mobiliario, PropiedadMobiliario


class PropiedadDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropiedadDetalle
        fields = ("id", "clave", "valor")


class PropiedadMobiliarioSerializer(serializers.ModelSerializer):
    mobiliario_nombre = serializers.CharField(
        source="mobiliario.nombre", read_only=True,
    )

    class Meta:
        model = PropiedadMobiliario
        fields = (
            "id", "propiedad", "mobiliario", "mobiliario_nombre",
            "cantidad", "valor_estimado", "estado",
        )


class PropiedadSerializer(serializers.ModelSerializer):
    detalles = PropiedadDetalleSerializer(many=True, read_only=True)
    mobiliarios = PropiedadMobiliarioSerializer(many=True, read_only=True)

    class Meta:
        model = Propiedad
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class PropiedadListSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(
        source="propietario.__str__", read_only=True,
    )

    class Meta:
        model = Propiedad
        fields = (
            "id", "nombre", "ciudad", "estado_geografico",
            "tipo", "costo_renta", "estado", "propietario_nombre",
        )


class MobiliarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobiliario
        fields = "__all__"
