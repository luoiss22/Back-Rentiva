from rest_framework import serializers
from .models import Especialista, ReporteMantenimiento, ResenaEspecialista


class EspecialistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialista
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class EspecialistaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialista
        fields = (
            "id", "nombre", "especialidad", "ciudad",
            "calificacion", "disponible",
        )


class ResenaEspecialistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResenaEspecialista
        fields = "__all__"
        read_only_fields = ("created_at",)


class ReporteMantenimientoSerializer(serializers.ModelSerializer):
    resenas = ResenaEspecialistaSerializer(many=True, read_only=True)
    especialista_nombre = serializers.CharField(
        source="especialista.nombre", read_only=True, default=None,
    )

    class Meta:
        model = ReporteMantenimiento
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ReporteMantenimientoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteMantenimiento
        fields = (
            "id", "propiedad", "especialista", "prioridad",
            "estado", "created_at",
        )
