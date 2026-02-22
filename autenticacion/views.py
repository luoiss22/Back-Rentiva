from rest_framework import viewsets
from .models import Propietario, Credencial
from .serializers import (
    PropietarioSerializer,
    PropietarioListSerializer,
    CredencialSerializer,
)


class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    filterset_fields = ("estado", "rol")
    search_fields = ("nombre", "apellidos", "email")
    ordering_fields = ("nombre", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PropietarioListSerializer
        return PropietarioSerializer


class CredencialViewSet(viewsets.ModelViewSet):
    queryset = Credencial.objects.select_related("propietario").all()
    serializer_class = CredencialSerializer
