from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .authentication import get_tokens_for_propietario
from .models import Propietario, Credencial
from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    PropietarioSerializer,
    PropietarioListSerializer,
    RegistroSerializer,
    LoginSerializer,
    CambioPasswordSerializer,
)


# ── Auth views (públicas) ─────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def registro_view(request):
    """Crea Propietario + Credencial y devuelve tokens JWT."""
    serializer = RegistroSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    propietario = serializer.save()

    return Response(
        {
            "propietario": PropietarioSerializer(propietario).data,
            "tokens": get_tokens_for_propietario(propietario),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """Valida credenciales y devuelve tokens JWT."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    propietario = serializer.validated_data["propietario"]

    return Response({
        "propietario": PropietarioSerializer(propietario).data,
        "tokens": get_tokens_for_propietario(propietario),
    })


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET: perfil del propietario autenticado. PATCH: actualizar perfil."""
    if request.method == "PATCH":
        serializer = PropietarioSerializer(
            request.user, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(PropietarioSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cambio_password_view(request):
    """Cambia la contraseña del propietario autenticado."""
    request.propietario = request.user
    serializer = CambioPasswordSerializer(
        data=request.data, context={"request": request},
    )
    serializer.is_valid(raise_exception=True)

    credencial = request.user.credencial
    credencial.set_password(serializer.validated_data["password_nuevo"])
    credencial.save(update_fields=["contrasena_hash", "updated_at"])

    return Response({"detail": "Contraseña actualizada correctamente."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Invalida el refresh token (lo agrega a la blacklist)."""
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"refresh": "Este campo es requerido."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response(
            {"detail": "Token inválido o ya expirado."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({"detail": "Sesión cerrada correctamente."})


# ── Admin-only: cambiar rol ───────────────────────────────────────

@api_view(["PATCH"])
@permission_classes([IsAdmin])
def cambiar_rol_view(request, pk):
    """Solo admin puede cambiar el rol de un propietario."""
    try:
        propietario = Propietario.objects.get(pk=pk)
    except Propietario.DoesNotExist:
        return Response(
            {"detail": "Propietario no encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )

    nuevo_rol = request.data.get("rol")
    if nuevo_rol not in dict(Propietario.Rol.choices):
        return Response(
            {"rol": f"Rol inválido. Opciones: {list(dict(Propietario.Rol.choices).keys())}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    propietario.rol = nuevo_rol
    propietario.save(update_fields=["rol", "updated_at"])
    return Response(PropietarioSerializer(propietario).data)


# ── CRUD ViewSets (protegidos) ────────────────────────────────────

class PropietarioViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los propietarios.
    Propietario: solo puede verse a sí mismo.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado", "rol")
    search_fields = ("nombre", "apellidos", "email")
    ordering_fields = ("nombre", "created_at")

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return Propietario.objects.all()
        return Propietario.objects.filter(pk=user.pk)

    def get_serializer_class(self):
        if self.action == "list":
            return PropietarioListSerializer
        return PropietarioSerializer

    def get_owner_id(self, obj):
        return obj.pk
