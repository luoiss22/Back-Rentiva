from django.contrib import admin
from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo_entidad", "entidad_id", "tipo_documento", "nombre_archivo", "created_at")
    list_filter = ("tipo_entidad", "tipo_documento")
    search_fields = ("nombre_archivo", "descripcion")
