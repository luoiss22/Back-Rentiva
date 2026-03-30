from rest_framework import serializers
from autenticacion.models import Administrador
from .models import Propiedad, PropiedadDetalle, Mobiliario, PropiedadMobiliario, FotoPropiedad


class FotoPropiedadSerializer(serializers.ModelSerializer):
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = FotoPropiedad
        fields = ("id", "propiedad", "imagen", "descripcion", "es_principal", "orden", "created_at")
        read_only_fields = ("created_at",)

    def get_imagen(self, obj):
        if obj.imagen:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.imagen.url) if request else obj.imagen.url
        return None

    def validate_propiedad(self, propiedad):
        return _validate_propiedad_ownership(self, propiedad)


class PropiedadDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropiedadDetalle
        fields = ("id", "propiedad", "clave", "valor")

    def validate_propiedad(self, propiedad):
        return _validate_propiedad_ownership(self, propiedad)


def _validate_propiedad_ownership(serializer_self, propiedad):
    """Valida que la propiedad pertenece al usuario autenticado."""
    request = serializer_self.context.get("request")
    user = getattr(request, "user", None) if request else None
    if user and not isinstance(user, Administrador):
        if propiedad.propietario_id != user.pk:
            raise serializers.ValidationError(
                "No puedes operar sobre propiedades ajenas."
            )
    return propiedad


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

    def validate_propiedad(self, propiedad):
        return _validate_propiedad_ownership(self, propiedad)


class PropiedadSerializer(serializers.ModelSerializer):
    detalles = PropiedadDetalleSerializer(many=True, read_only=True)
    mobiliarios = PropiedadMobiliarioSerializer(many=True, read_only=True)
    fotos = FotoPropiedadSerializer(many=True, read_only=True)
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = Propiedad
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "propietario")

    def get_imagen(self, obj):
        foto = obj.fotos.filter(es_principal=True).first() or obj.fotos.first()
        if foto and foto.imagen:
            request = self.context.get("request")
            return request.build_absolute_uri(foto.imagen.url) if request else foto.imagen.url
        return None


class PropiedadListSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(
        source="propietario.__str__", read_only=True,
    )
    foto_principal = serializers.SerializerMethodField()

    class Meta:
        model = Propiedad
        fields = (
            "id", "nombre", "ciudad", "estado_geografico",
            "tipo", "costo_renta", "estado", "propietario_nombre", "foto_principal",
        )

    def get_foto_principal(self, obj):
        foto = obj.fotos.filter(es_principal=True).first() or obj.fotos.first()
        if foto and foto.imagen:
            request = self.context.get("request")
            return request.build_absolute_uri(foto.imagen.url) if request else foto.imagen.url
        return None


class MobiliarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobiliario
        fields = "__all__"
