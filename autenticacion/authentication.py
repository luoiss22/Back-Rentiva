"""
Custom JWT authentication for Propietario (non-Django-User model).

simplejwt expects Django's User model by default. This module overrides
the authentication class so it looks up Propietario instead.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import Propietario


class PropietarioJWTAuthentication(JWTAuthentication):
    """
    Autentica requests usando JWT pero busca en Propietario
    en lugar de auth.User.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if user_id is None:
            return None
        try:
            propietario = Propietario.objects.get(pk=user_id)
        except Propietario.DoesNotExist:
            return None
        if propietario.estado == propietario.Estado.SUSPENDIDO:
            return None
        return propietario


def get_tokens_for_propietario(propietario: Propietario) -> dict:
    """Genera access + refresh tokens para un Propietario."""
    refresh = RefreshToken()
    refresh["user_id"] = propietario.pk
    refresh["email"] = propietario.email
    refresh["rol"] = propietario.rol
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
