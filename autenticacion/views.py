from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .authentication import get_tokens_for_admin, get_tokens_for_propietario
from .models import Administrador, Propietario
from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    AdministradorSerializer,
    AdministradorListSerializer,
    RegistroAdminSerializer,
    PropietarioSerializer,
    PropietarioListSerializer,
    RegistroSerializer,
    LoginSerializer,
    CambioPasswordSerializer,
)


# ── Login unificado ───────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """Login unificado: detecta si es admin o propietario."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    usuario = serializer.validated_data["usuario"]
    user_type = serializer.validated_data["user_type"]

    if user_type == "admin":
        tokens = get_tokens_for_admin(usuario)
        user_data = AdministradorSerializer(usuario).data
    else:
        tokens = get_tokens_for_propietario(usuario)
        user_data = PropietarioSerializer(usuario).data

    return Response({
        "usuario": user_data,
        "user_type": user_type,
        "tokens": tokens,
    })


# ── Registro de propietario (publico) ─────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def registro_view(request):
    """Crea Propietario + Credencial y devuelve tokens JWT."""
    serializer = RegistroSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    propietario = serializer.save()

    return Response(
        {
            "usuario": PropietarioSerializer(propietario).data,
            "user_type": "propietario",
            "tokens": get_tokens_for_propietario(propietario),
        },
        status=status.HTTP_201_CREATED,
    )


# ── Perfil autenticado (ambos tipos) ─────────────────────────────

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET: perfil del usuario autenticado. PATCH: actualizar perfil."""
    user = request.user
    is_admin = isinstance(user, Administrador)
    SerializerClass = AdministradorSerializer if is_admin else PropietarioSerializer

    if request.method == "PATCH":
        # Los propietarios pueden actualizar también sus datos bancarios.
        CAMPOS_PERMITIDOS = {
            "nombre", "apellidos", "fecha_nacimiento", "telefono", "email", "folio_ine",
        }
        if not is_admin:
            CAMPOS_PERMITIDOS.update({"banco", "clabe_interbancaria", "foto"})
        data_filtrada = {k: v for k, v in request.data.items() if k in CAMPOS_PERMITIDOS}
        serializer = SerializerClass(user, data=data_filtrada, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "usuario": SerializerClass(user).data,
            "user_type": "admin" if is_admin else "propietario",
        })

    return Response({
        "usuario": SerializerClass(user).data,
        "user_type": "admin" if is_admin else "propietario",
    })


# ── Cambio de password (ambos tipos) ─────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cambio_password_view(request):
    """Cambia la contrasena del usuario autenticado."""
    serializer = CambioPasswordSerializer(
        data=request.data, context={"request": request},
    )
    serializer.is_valid(raise_exception=True)

    credencial = request.user.credencial
    credencial.set_password(serializer.validated_data["password_nuevo"])
    credencial.save(update_fields=["contrasena_hash", "updated_at"])

    return Response({"detail": "Contrasena actualizada correctamente."})


# ── Logout ────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Invalida el refresh token."""
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
            {"detail": "Token invalido o ya expirado."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({"detail": "Sesion cerrada correctamente."})


# ── CRUD Administradores (solo admin) ─────────────────────────────

@api_view(["POST"])
@permission_classes([IsAdmin])
def registro_admin_view(request):
    """Solo un admin puede crear otro admin."""
    serializer = RegistroAdminSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    admin = serializer.save()
    return Response(
        AdministradorSerializer(admin).data,
        status=status.HTTP_201_CREATED,
    )


class AdministradorViewSet(viewsets.ModelViewSet):
    """CRUD de administradores. Solo accesible por admins."""
    queryset = Administrador.objects.all()
    permission_classes = [IsAdmin]
    filterset_fields = ("estado",)
    search_fields = ("nombre", "apellidos", "email")
    ordering_fields = ("nombre", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return AdministradorListSerializer
        return AdministradorSerializer


# ── CRUD Propietarios ─────────────────────────────────────────────

class PropietarioViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los propietarios.
    Propietario: solo puede verse a si mismo.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado",)
    search_fields = ("nombre", "apellidos", "email")
    ordering_fields = ("nombre", "created_at")

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, Administrador):
            return Propietario.objects.all()
        return Propietario.objects.filter(pk=user.pk)

    def get_serializer_class(self):
        if self.action == "list":
            return PropietarioListSerializer
        return PropietarioSerializer

    def get_owner_id(self, obj):
        return obj.pk
