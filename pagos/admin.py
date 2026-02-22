from django.contrib import admin
from .models import Pago, FichaPago, Factura


class FichaPagoInline(admin.StackedInline):
    model = FichaPago
    extra = 0


class FacturaInline(admin.StackedInline):
    model = Factura
    extra = 0


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "contrato", "periodo", "monto",
        "fecha_limite", "fecha_pago", "estado",
    )
    list_filter = ("estado", "metodo_pago")
    search_fields = ("periodo", "referencia")
    inlines = [FichaPagoInline, FacturaInline]


@admin.register(FichaPago)
class FichaPagoAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "codigo_referencia", "banco", "fecha_generacion")
    search_fields = ("codigo_referencia",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "folio_fiscal", "total", "fecha_emision")
    search_fields = ("folio_fiscal",)
