from django.db import transaction
from rest_framework import serializers
from .models import Propietario, Credencial


class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "rol")


class PropietarioListSerializer(serializers.ModelSerializer):
    """Versión ligera para listados."""

    class Meta:
        model = Propietario
        fields = ("id", "nombre", "apellidos", "email", "telefono", "estado")


# ── Auth serializers ───────────────────────────────────────────────

class RegistroSerializer(serializers.Serializer):
    """Registro: crea Propietario + Credencial en una transacción."""

    nombre = serializers.CharField(max_length=120)
    apellidos = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=20, required=False, default="")
    folio_ine = serializers.CharField(max_length=20, required=False, default="")
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if Propietario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este correo.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        with transaction.atomic():
            propietario = Propietario.objects.create(
                rol=Propietario.Rol.PROPIETARIO,  # Siempre propietario
                **validated_data,
            )
            credencial = Credencial(
                propietario=propietario,
                email=propietario.email,
            )
            credencial.set_password(password)
            credencial.save()
        return propietario


class LoginSerializer(serializers.Serializer):
    """Valida credenciales y devuelve el propietario."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    MAX_INTENTOS = 5

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        try:
            credencial = Credencial.objects.select_related("propietario").get(email=email)
        except Credencial.DoesNotExist:
            raise serializers.ValidationError({"email": "Credenciales inválidas."})

        if credencial.bloqueado:
            raise serializers.ValidationError(
                {"email": "Cuenta bloqueada por demasiados intentos fallidos. Contacta soporte."}
            )

        if not credencial.check_password(password):
            credencial.intentos_fallidos += 1
            if credencial.intentos_fallidos >= self.MAX_INTENTOS:
                credencial.bloqueado = True
            credencial.save(update_fields=["intentos_fallidos", "bloqueado"])
            raise serializers.ValidationError({"password": "Credenciales inválidas."})

        # Reset intentos en login exitoso
        from django.utils import timezone
        credencial.intentos_fallidos = 0
        credencial.ultimo_acceso = timezone.now()
        credencial.save(update_fields=["intentos_fallidos", "ultimo_acceso"])

        attrs["propietario"] = credencial.propietario
        return attrs


class CambioPasswordSerializer(serializers.Serializer):
    """Cambio de contraseña autenticado."""

    password_actual = serializers.CharField(write_only=True)
    password_nuevo = serializers.CharField(write_only=True, min_length=8)

    def validate_password_actual(self, value):
        propietario = self.context["request"].propietario
        credencial = propietario.credencial
        if not credencial.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
