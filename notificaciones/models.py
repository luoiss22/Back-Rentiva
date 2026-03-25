from django.db import models


class Notificacion(models.Model):
    """Notificación / recordatorio programado vinculado a un contrato."""

    class TipoNotificacion(models.TextChoices):
        PAGO_PROXIMO = "pago_proximo", "Pago próximo"
        PAGO_VENCIDO = "pago_vencido", "Pago vencido"
        CONTRATO_VENCER = "contrato_por_vencer", "Contrato por vencer"
        GENERAL = "general", "General"

    class Medio(models.TextChoices):
        EMAIL = "email", "Correo electrónico"
        SMS = "sms", "SMS"
        PUSH = "push", "Notificación push"
        WHATSAPP = "whatsapp", "WhatsApp"

    contrato = models.ForeignKey(
        "contratos.Contrato",
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    tipo = models.CharField(
        max_length=25, choices=TipoNotificacion.choices,
    )
    titulo = models.CharField(max_length=200, blank=True)
    mensaje = models.TextField(blank=True)
    fecha_programada = models.DateTimeField()
    medio = models.CharField(max_length=15, choices=Medio.choices, default=Medio.EMAIL)
    leida = models.BooleanField(default=False, help_text="Indica si el usuario ya vio esta notificación en la app")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notificaciones"
        ordering = ["-fecha_programada"]
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.tipo} — {self.fecha_programada:%Y-%m-%d}"


class NotificacionLog(models.Model):
    """Log de cada intento de envío de una notificación."""

    class Estado(models.TextChoices):
        ENVIADO = "enviado", "Enviado"
        FALLIDO = "fallido", "Fallido"
        PENDIENTE = "pendiente", "Pendiente"

    notificacion = models.ForeignKey(
        Notificacion,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    intento_numero = models.PositiveSmallIntegerField(default=1)
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.PENDIENTE,
    )
    mensaje_error = models.TextField(blank=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notificacion_logs"
        ordering = ["intento_numero"]
        verbose_name = "Log de notificación"
        verbose_name_plural = "Logs de notificaciones"

    def __str__(self):
        return f"Intento {self.intento_numero} — {self.estado}"
