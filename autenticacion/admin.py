from django.contrib import admin
from .models import Administrador, CredencialAdmin as CredencialAdminModel, Propietario, Credencial


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellidos", "email", "estado", "created_at")
    list_filter = ("estado",)
    search_fields = ("nombre", "apellidos", "email")


@admin.register(CredencialAdminModel)
class CredencialAdminModelAdmin(admin.ModelAdmin):
    list_display = ("id", "administrador", "email", "ultimo_acceso", "bloqueado")
    list_filter = ("bloqueado",)
    search_fields = ("email",)


@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellidos", "email", "estado", "created_at")
    list_filter = ("estado",)
    search_fields = ("nombre", "apellidos", "email")


@admin.register(Credencial)
class CredencialModelAdmin(admin.ModelAdmin):
    list_display = ("id", "propietario", "email", "ultimo_acceso", "bloqueado")
    list_filter = ("bloqueado",)
    search_fields = ("email",)
