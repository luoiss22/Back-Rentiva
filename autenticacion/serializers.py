from rest_framework import serializers
from .models import Propietario, Credencial


class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class PropietarioListSerializer(serializers.ModelSerializer):
    """Versión ligera para listados."""

    class Meta:
        model = Propietario
        fields = ("id", "nombre", "apellidos", "email", "telefono", "estado")


class CredencialSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Credencial
        fields = (
            "id", "propietario", "email", "password",
            "ultimo_acceso", "intentos_fallidos", "bloqueado",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "contrasena_hash", "ultimo_acceso",
            "intentos_fallidos", "bloqueado",
            "created_at", "updated_at",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        credencial = Credencial(**validated_data)
        credencial.set_password(password)
        credencial.save()
        return credencial

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
