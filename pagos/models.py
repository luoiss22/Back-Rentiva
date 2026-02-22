from django.db import models


class Pago(models.Model):
    """Registro de pago de renta por periodo."""

    class MetodoPago(models.TextChoices):
        TRANSFERENCIA = "transferencia", "Transferencia bancaria"
        EFECTIVO = "efectivo", "Efectivo"
        DEPOSITO = "deposito", "Depósito bancario"
        TARJETA = "tarjeta", "Tarjeta"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO = "pagado", "Pagado"
        VENCIDO = "vencido", "Vencido"
        PARCIAL = "parcial", "Pago parcial"
        CANCELADO = "cancelado", "Cancelado"

    contrato = models.ForeignKey(
        "contratos.Contrato",
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    periodo = models.CharField(
        max_length=30,
        help_text="Identificador del periodo, ej: 2026-03, 2026-03-15",
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_limite = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)
    metodo_pago = models.CharField(
        max_length=20, choices=MetodoPago.choices, blank=True,
    )
    referencia = models.CharField(max_length=100, blank=True)
    comprobante_url = models.FileField(
        upload_to="comprobantes/", blank=True, null=True,
    )
    recargo_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.PENDIENTE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pagos"
        ordering = ["-fecha_limite"]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago {self.periodo} — {self.estado} (${self.monto})"


class FichaPago(models.Model):
    """Formato / ficha de pago para depósito bancario o ventanilla."""

    pago = models.OneToOneField(
        Pago,
        on_delete=models.CASCADE,
        related_name="ficha",
    )
    codigo_referencia = models.CharField(max_length=50)
    clabe_interbancaria = models.CharField("CLABE interbancaria", max_length=18)
    banco = models.CharField(max_length=100)
    archivo_pdf = models.FileField(upload_to="fichas_pago/", blank=True, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fichas_pago"
        verbose_name = "Ficha de pago"
        verbose_name_plural = "Fichas de pago"

    def __str__(self):
        return f"Ficha #{self.pk} — Ref: {self.codigo_referencia}"


class Factura(models.Model):
    """Factura electrónica (CFDI) asociada a un pago."""

    pago = models.OneToOneField(
        Pago,
        on_delete=models.CASCADE,
        related_name="factura",
    )
    folio_fiscal = models.CharField(max_length=100, unique=True)
    datos_fiscales_emisor = models.ForeignKey(
        "fiscal.DatosFiscales",
        on_delete=models.PROTECT,
        related_name="facturas_como_emisor",
    )
    datos_fiscales_receptor = models.ForeignKey(
        "fiscal.DatosFiscales",
        on_delete=models.PROTECT,
        related_name="facturas_como_receptor",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    xml_path = models.FileField(upload_to="facturas/xml/", blank=True, null=True)
    pdf_path = models.FileField(upload_to="facturas/pdf/", blank=True, null=True)
    fecha_emision = models.DateTimeField()

    class Meta:
        db_table = "facturas"
        ordering = ["-fecha_emision"]
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"Factura {self.folio_fiscal} — ${self.total}"
