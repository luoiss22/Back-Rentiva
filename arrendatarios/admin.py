from django.contrib import admin
from .models import Arrendatario


@admin.register(Arrendatario)
class ArrendatarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellidos", "email", "telefono", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre", "apellidos", "email", "folio_ine")
