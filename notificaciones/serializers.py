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

    def validate_contrato(self, contrato):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "rol", None) != "admin":
            if contrato.propiedad.propietario_id != user.pk:
                raise serializers.ValidationError(
                    "No puedes crear notificaciones en contratos ajenos."
                )
        return contrato


class NotificacionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = (
            "id", "contrato", "tipo", "titulo",
            "fecha_programada", "medio",
        )
