from django.contrib import admin
from .models import Contrato, HistorialContrato


class HistorialContratoInline(admin.TabularInline):
    model = HistorialContrato
    extra = 0
    readonly_fields = ("estado_anterior", "estado_nuevo", "motivo", "fecha_cambio")


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "propiedad", "arrendatario",
        "fecha_inicio", "fecha_fin", "renta_acordada",
        "periodo_pago", "estado",
    )
    list_filter = ("estado", "periodo_pago")
    search_fields = ("propiedad__nombre", "arrendatario__nombre")
    inlines = [HistorialContratoInline]
