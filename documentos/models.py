from django.db import models


class Documento(models.Model):
    """
    Documento adjunto polimórfico — puede vincularse a cualquier
    entidad del sistema (Propiedad, Contrato, Arrendatario, etc.).
    """

    class TipoEntidad(models.TextChoices):
        PROPIEDAD = "propiedad", "Propiedad"
        CONTRATO = "contrato", "Contrato"
        ARRENDATARIO = "arrendatario", "Arrendatario"
        PROPIETARIO = "propietario", "Propietario"
        REPORTE = "reporte", "Reporte de mantenimiento"

    class TipoDocumento(models.TextChoices):
        CONTRATO_PDF = "contrato_pdf", "Contrato PDF"
        INE = "ine", "INE"
        COMPROBANTE_DOMICILIO = "comprobante_domicilio", "Comprobante de domicilio"
        FOTO = "foto", "Fotografía"
        ESCRITURA = "escritura", "Escritura"
        OTRO = "otro", "Otro"

    tipo_entidad = models.CharField(max_length=20, choices=TipoEntidad.choices)
    entidad_id = models.PositiveBigIntegerField(
        help_text="PK de la entidad asociada",
    )
    tipo_documento = models.CharField(max_length=30, choices=TipoDocumento.choices)
    nombre_archivo = models.CharField(max_length=255)
    ruta_archivo = models.FileField(upload_to="documentos/")
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "documentos"
        ordering = ["-created_at"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        indexes = [
            models.Index(fields=["tipo_entidad", "entidad_id"]),
        ]

    def __str__(self):
        return f"{self.tipo_documento} — {self.nombre_archivo}"
