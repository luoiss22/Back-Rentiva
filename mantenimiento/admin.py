from django.contrib import admin
from .models import Especialista, ReporteMantenimiento, ResenaEspecialista


@admin.register(Especialista)
class EspecialistaAdmin(admin.ModelAdmin):
    list_display = (
        "id", "nombre", "especialidad", "ciudad",
        "calificacion", "disponible",
    )
    list_filter = ("especialidad", "disponible")
    search_fields = ("nombre", "especialidad")


class ResenaInline(admin.TabularInline):
    model = ResenaEspecialista
    extra = 0
    fk_name = "reporte"


@admin.register(ReporteMantenimiento)
class ReporteMantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "propiedad", "especialista",
        "prioridad", "estado", "created_at",
    )
    list_filter = ("estado", "prioridad")
    search_fields = ("descripcion",)
    inlines = [ResenaInline]


@admin.register(ResenaEspecialista)
class ResenaEspecialistaAdmin(admin.ModelAdmin):
    list_display = ("id", "especialista", "propietario", "calificacion", "created_at")
    list_filter = ("calificacion",)
