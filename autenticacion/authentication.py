"""
Custom JWT authentication that supports two user types:
Administrador and Propietario, each with their own table.

The token includes a 'user_type' claim ('admin' or 'propietario')
so the authentication class knows which table to query.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Administrador, Propietario


class MultiUserJWTAuthentication(JWTAuthentication):
    """
    Autentica requests usando JWT. Usa el claim 'user_type'
    para decidir si buscar en Administrador o Propietario.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        user_type = validated_token.get("user_type", "propietario")
        if user_id is None:
            return None

        try:
            if user_type == "admin":
                user = Administrador.objects.get(pk=user_id)
            else:
                user = Propietario.objects.get(pk=user_id)
        except (Administrador.DoesNotExist, Propietario.DoesNotExist):
            return None

        if getattr(user, "estado", None) == "suspendido":
            return None
        return user


def get_tokens_for_admin(admin: Administrador) -> dict:
    """Genera access + refresh tokens para un Administrador."""
    refresh = RefreshToken()
    refresh["user_id"] = admin.pk
    refresh["email"] = admin.email
    refresh["user_type"] = "admin"
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def get_tokens_for_propietario(propietario: Propietario) -> dict:
    """Genera access + refresh tokens para un Propietario."""
    refresh = RefreshToken()
    refresh["user_id"] = propietario.pk
    refresh["email"] = propietario.email
    refresh["user_type"] = "propietario"
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
