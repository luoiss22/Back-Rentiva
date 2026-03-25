from rest_framework import serializers
from .models import Arrendatario


class ArrendatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arrendatario
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "propietario")


class ArrendatarioListSerializer(serializers.ModelSerializer):
    propiedad_actual = serializers.SerializerMethodField()

    class Meta:
        model = Arrendatario
        fields = ("id", "nombre", "apellidos", "email", "telefono", "estado", "propiedad_actual")

    def get_propiedad_actual(self, obj):
        contrato = obj.contratos.filter(estado="activo").first()
        if contrato:
            return contrato.propiedad.nombre
        return "Sin propiedad"
