from django.contrib import admin
from .models import Propiedad, PropiedadDetalle, Mobiliario, PropiedadMobiliario, FotoPropiedad


class PropiedadDetalleInline(admin.TabularInline):
    model = PropiedadDetalle
    extra = 1


class PropiedadMobiliarioInline(admin.TabularInline):
    model = PropiedadMobiliario
    extra = 1


class FotoPropiedadInline(admin.TabularInline):
    model = FotoPropiedad
    extra = 1
    fields = ("imagen", "descripcion", "es_principal", "orden")


@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "ciudad", "tipo", "costo_renta", "estado", "propietario")
    list_filter = ("estado", "tipo", "ciudad")
    search_fields = ("nombre", "direccion", "ciudad")
    inlines = [FotoPropiedadInline, PropiedadDetalleInline, PropiedadMobiliarioInline]


@admin.register(Mobiliario)
class MobiliarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo")
    search_fields = ("nombre",)


@admin.register(FotoPropiedad)
class FotoPropiedadAdmin(admin.ModelAdmin):
    list_display = ("id", "propiedad", "es_principal", "orden", "created_at")
    list_filter = ("es_principal",)
    search_fields = ("propiedad__nombre",)
