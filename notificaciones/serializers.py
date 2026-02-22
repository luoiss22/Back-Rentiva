from rest_framework import serializers
from .models import Notificacion, NotificacionLog


class NotificacionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionLog
        fields = "__all__"
        read_only_fields = ("fecha_envio",)


class NotificacionSerializer(serializers.ModelSerializer):
    logs = NotificacionLogSerializer(many=True, read_only=True)

    class Meta:
        model = Notificacion
        fields = "__all__"
        read_only_fields = ("created_at",)


class NotificacionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = (
            "id", "contrato", "tipo", "titulo",
            "fecha_programada", "medio",
        )
