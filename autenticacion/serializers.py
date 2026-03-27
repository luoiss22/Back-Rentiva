from django.db import transaction
from rest_framework import serializers
from .models import Administrador, CredencialAdmin, Propietario, Credencial


# ── Administrador serializers ──────────────────────────────────────

class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class AdministradorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = ("id", "nombre", "apellidos", "email", "telefono", "estado")


class RegistroAdminSerializer(serializers.Serializer):
    """Registro de admin: crea Administrador + CredencialAdmin."""

    nombre = serializers.CharField(max_length=120)
    apellidos = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=20, required=False, default="")
    folio_ine = serializers.CharField(max_length=20, required=False, default="")
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if Administrador.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un admin con este correo.")
        if Propietario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un propietario con este correo.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        with transaction.atomic():
            admin = Administrador.objects.create(**validated_data)
            cred = CredencialAdmin(administrador=admin, email=admin.email)
            cred.set_password(password)
            cred.save()
        return admin


# ── Propietario serializers ────────────────────────────────────────

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class PropietarioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = ("id", "nombre", "apellidos", "email", "telefono", "estado")


class RegistroSerializer(serializers.Serializer):
    """Registro de propietario: crea Propietario + Credencial."""

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
        if Administrador.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un admin con este correo.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        with transaction.atomic():
            propietario = Propietario.objects.create(**validated_data)
            credencial = Credencial(
                propietario=propietario,
                email=propietario.email,
            )
            credencial.set_password(password)
            credencial.save()
        return propietario


# ── Login unificado ────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    """
    Login unificado: busca primero en CredencialAdmin, luego en Credencial.
    Devuelve el usuario y su tipo.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    MAX_INTENTOS = 5

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        # Intentar como admin primero
        try:
            cred = CredencialAdmin.objects.select_related("administrador").get(email=email)
            return self._validar_credencial(cred, password, cred.administrador, "admin")
        except CredencialAdmin.DoesNotExist:
            pass

        # Intentar como propietario
        try:
            cred = Credencial.objects.select_related("propietario").get(email=email)
            return self._validar_credencial(cred, password, cred.propietario, "propietario")
        except Credencial.DoesNotExist:
            raise serializers.ValidationError({"email": "Credenciales invalidas."})

    def _validar_credencial(self, credencial, password, usuario, user_type):
        if credencial.bloqueado:
            raise serializers.ValidationError(
                {"email": "Cuenta bloqueada por demasiados intentos fallidos. Contacta soporte."}
            )

        if not credencial.check_password(password):
            credencial.intentos_fallidos += 1
            if credencial.intentos_fallidos >= self.MAX_INTENTOS:
                credencial.bloqueado = True
            credencial.save(update_fields=["intentos_fallidos", "bloqueado"])
            raise serializers.ValidationError({"password": "Credenciales invalidas."})

        from django.utils import timezone
        credencial.intentos_fallidos = 0
        credencial.ultimo_acceso = timezone.now()
        credencial.save(update_fields=["intentos_fallidos", "ultimo_acceso"])

        return {"usuario": usuario, "user_type": user_type}


class CambioPasswordSerializer(serializers.Serializer):
    """Cambio de contrasena autenticado (funciona para ambos tipos)."""

    password_actual = serializers.CharField(write_only=True)
    password_nuevo = serializers.CharField(write_only=True, min_length=8)

    def validate_password_actual(self, value):
        user = self.context["request"].user
        credencial = user.credencial
        if not credencial.check_password(value):
            raise serializers.ValidationError("La contrasena actual es incorrecta.")
        return value
