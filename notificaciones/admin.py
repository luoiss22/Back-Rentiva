from django.contrib import admin
from .models import Notificacion, NotificacionLog


class NotificacionLogInline(admin.TabularInline):
    model = NotificacionLog
    extra = 0
    readonly_fields = ("intento_numero", "estado", "mensaje_error", "fecha_envio")


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "contrato", "tipo", "medio", "fecha_programada")
    list_filter = ("tipo", "medio")
    inlines = [NotificacionLogInline]
