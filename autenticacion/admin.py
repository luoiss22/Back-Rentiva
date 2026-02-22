from django.contrib import admin
from .models import Propietario, Credencial


@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellidos", "email", "rol", "estado", "created_at")
    list_filter = ("estado", "rol")
    search_fields = ("nombre", "apellidos", "email")


@admin.register(Credencial)
class CredencialAdmin(admin.ModelAdmin):
    list_display = ("id", "propietario", "email", "ultimo_acceso", "bloqueado")
    list_filter = ("bloqueado",)
    search_fields = ("email",)
