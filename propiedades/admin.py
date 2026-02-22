from django.contrib import admin
from .models import Propiedad, PropiedadDetalle, Mobiliario, PropiedadMobiliario


class PropiedadDetalleInline(admin.TabularInline):
    model = PropiedadDetalle
    extra = 1


class PropiedadMobiliarioInline(admin.TabularInline):
    model = PropiedadMobiliario
    extra = 1


@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "ciudad", "tipo", "costo_renta", "estado", "propietario")
    list_filter = ("estado", "tipo", "ciudad")
    search_fields = ("nombre", "direccion", "ciudad")
    inlines = [PropiedadDetalleInline, PropiedadMobiliarioInline]


@admin.register(Mobiliario)
class MobiliarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo")
    search_fields = ("nombre",)
