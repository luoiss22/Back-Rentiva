"""
Permisos personalizados basados en el rol del Propietario.

- IsAdmin: solo usuarios con rol=admin
- IsAdminOrReadOnly: admin puede escribir, propietario solo leer
- IsOwnerOrAdmin: propietario solo accede a sus propios recursos; admin a todo
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Solo permite acceso a usuarios con rol=admin (la empresa)."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "rol")
            and request.user.rol == "admin"
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin puede hacer todo; propietario solo lectura."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            hasattr(request.user, "rol")
            and request.user.rol == "admin"
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Admin accede a todo.
    Propietario solo accede a objetos que le pertenecen.

    Para object-level, el ViewSet debe definir get_owner_id(obj)
    o el objeto debe tener un campo `propietario` o `propietario_id`.
    """

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "is_authenticated", False))

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, "rol") and request.user.rol == "admin":
            return True
        # Intentar obtener el propietario_id del objeto
        owner_id = _get_owner_id(view, obj)
        return owner_id == request.user.pk


def _get_owner_id(view, obj):
    """Resuelve el propietario_id de un objeto según convenciones."""
    # Si el ViewSet define explícitamente cómo obtener el owner
    if hasattr(view, "get_owner_id"):
        return view.get_owner_id(obj)
    # Convenciones comunes
    if hasattr(obj, "propietario_id"):
        return obj.propietario_id
    if hasattr(obj, "propiedad") and hasattr(obj.propiedad, "propietario_id"):
        return obj.propiedad.propietario_id
    if hasattr(obj, "contrato") and hasattr(obj.contrato, "propiedad"):
        return obj.contrato.propiedad.propietario_id
    return None
