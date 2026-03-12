from rest_framework import viewsets

from autenticacion.permissions import IsOwnerOrAdmin
from .models import Arrendatario
from .serializers import ArrendatarioSerializer, ArrendatarioListSerializer


class ArrendatarioViewSet(viewsets.ModelViewSet):
    """
    Admin: ve todos los arrendatarios.
    Propietario: solo ve los arrendatarios que él registró.
    """
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ("estado",)
    search_fields = ("nombre", "apellidos", "email", "folio_ine")
    ordering_fields = ("nombre", "apellidos", "created_at")

    def get_queryset(self):
        qs = Arrendatario.objects.select_related("propietario")
        user = self.request.user
        if getattr(user, "rol", None) == "admin":
            return qs
        return qs.filter(propietario=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ArrendatarioListSerializer
        return ArrendatarioSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "rol", None) != "admin":
            serializer.save(propietario=user)
        else:
            serializer.save()
