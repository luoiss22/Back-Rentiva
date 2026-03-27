"""
Permisos personalizados basados en el tipo de usuario.

- IsAdmin: solo Administradores
- IsAdminOrReadOnly: admin puede escribir, propietario solo leer
- IsOwnerOrAdmin: propietario solo accede a sus propios recursos; admin a todo
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Administrador


def _is_admin(user):
    """Verifica si el user es un Administrador."""
    return isinstance(user, Administrador)


class IsAdmin(BasePermission):
    """Solo permite acceso a Administradores."""

    def has_permission(self, request, view):
        return _is_admin(request.user)


class IsAdminOrReadOnly(BasePermission):
    """Admin puede hacer todo; propietario solo lectura."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _is_admin(request.user)


class IsOwner(BasePermission):
    """Solo propietarios autenticados. Admins bloqueados completamente."""

    def has_permission(self, request, view):
        return (
            bool(request.user and getattr(request.user, "is_authenticated", False))
            and not _is_admin(request.user)
        )

    def has_object_permission(self, request, view, obj):
        owner_id = _get_owner_id(view, obj)
        return owner_id == request.user.pk


class IsOwnerOrAdmin(BasePermission):
    """
    Admin accede a todo.
    Propietario solo accede a objetos que le pertenecen.
    """

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "is_authenticated", False))

    def has_object_permission(self, request, view, obj):
        if _is_admin(request.user):
            return True
        owner_id = _get_owner_id(view, obj)
        return owner_id == request.user.pk


def _get_owner_id(view, obj):
    """Resuelve el propietario_id de un objeto segun convenciones."""
    if hasattr(view, "get_owner_id"):
        return view.get_owner_id(obj)
    if hasattr(obj, "propietario_id"):
        return obj.propietario_id
    if hasattr(obj, "propiedad") and hasattr(obj.propiedad, "propietario_id"):
        return obj.propiedad.propietario_id
    if hasattr(obj, "contrato") and hasattr(obj.contrato, "propiedad"):
        return obj.contrato.propiedad.propietario_id
    return None
