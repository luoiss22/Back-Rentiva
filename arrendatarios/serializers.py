from rest_framework import serializers
from .models import Arrendatario


class ArrendatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arrendatario
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ArrendatarioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arrendatario
        fields = ("id", "nombre", "apellidos", "email", "telefono", "estado")
