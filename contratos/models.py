from django.db import models


class Contrato(models.Model):
    """Contrato de arrendamiento entre propiedad y arrendatario."""

    class PeriodoPago(models.TextChoices):
        DIARIO = "diario", "Diario"
        MENSUAL = "mensual", "Mensual"
        ANUAL = "anual", "Anual"

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        ACTIVO = "activo", "Activo"
        FINALIZADO = "finalizado", "Finalizado"
        CANCELADO = "cancelado", "Cancelado"
        RENOVADO = "renovado", "Renovado"

    propiedad = models.ForeignKey(
        "propiedades.Propiedad",
        on_delete=models.CASCADE,
        related_name="contratos",
    )
    arrendatario = models.ForeignKey(
        "arrendatarios.Arrendatario",
        on_delete=models.CASCADE,
        related_name="contratos",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    renta_acordada = models.DecimalField(max_digits=12, decimal_places=2)
    deposito = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dia_pago = models.PositiveSmallIntegerField(
        help_text="Día del periodo en que se cobra (1-31 para mensual)",
    )
    periodo_pago = models.CharField(
        max_length=10, choices=PeriodoPago.choices, default=PeriodoPago.MENSUAL,
    )
    incremento_anual = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Porcentaje de incremento anual",
    )
    penalizacion_anticipada = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Penalización por terminación anticipada",
    )
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.BORRADOR,
    )
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contratos"
        ordering = ["-fecha_inicio"]
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return f"Contrato #{self.pk} — {self.propiedad} → {self.arrendatario}"


class HistorialContrato(models.Model):
    """Auditoría de cambios de estado en un contrato."""

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="historial",
    )
    estado_anterior = models.CharField(max_length=15)
    estado_nuevo = models.CharField(max_length=15)
    motivo = models.TextField(blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "historial_contratos"
        ordering = ["-fecha_cambio"]
        verbose_name = "Historial de contrato"
        verbose_name_plural = "Historial de contratos"

    def __str__(self):
        return f"{self.contrato} | {self.estado_anterior} → {self.estado_nuevo}"
