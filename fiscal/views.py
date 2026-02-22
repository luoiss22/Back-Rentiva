from rest_framework import viewsets
from .models import DatosFiscales
from .serializers import DatosFiscalesSerializer


class DatosFiscalesViewSet(viewsets.ModelViewSet):
    queryset = DatosFiscales.objects.all()
    serializer_class = DatosFiscalesSerializer
    filterset_fields = ("tipo_entidad", "entidad_id")
    search_fields = ("rfc", "nombre_o_razon_social")
