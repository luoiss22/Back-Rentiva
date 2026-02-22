from rest_framework import viewsets
from .models import Arrendatario
from .serializers import ArrendatarioSerializer, ArrendatarioListSerializer


class ArrendatarioViewSet(viewsets.ModelViewSet):
    queryset = Arrendatario.objects.all()
    filterset_fields = ("estado",)
    search_fields = ("nombre", "apellidos", "email", "folio_ine")
    ordering_fields = ("nombre", "apellidos", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return ArrendatarioListSerializer
        return ArrendatarioSerializer
