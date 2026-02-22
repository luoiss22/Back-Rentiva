from django.contrib import admin
from .models import DatosFiscales


@admin.register(DatosFiscales)
class DatosFiscalesAdmin(admin.ModelAdmin):
    list_display = ("id", "rfc", "nombre_o_razon_social", "tipo_entidad", "regimen_fiscal")
    list_filter = ("tipo_entidad",)
    search_fields = ("rfc", "nombre_o_razon_social")
