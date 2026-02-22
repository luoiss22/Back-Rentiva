from rest_framework import viewsets
from .models import Documento
from .serializers import DocumentoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    filterset_fields = ("tipo_entidad", "entidad_id", "tipo_documento")
    search_fields = ("nombre_archivo", "descripcion")
