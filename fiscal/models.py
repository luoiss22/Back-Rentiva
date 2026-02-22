from django.db import models


class DatosFiscales(models.Model):
    """
    Datos fiscales polimórficos — pueden pertenecer a un Propietario
    (emisor) o a un Arrendatario (receptor).
    """

    class TipoEntidad(models.TextChoices):
        PROPIETARIO = "propietario", "Propietario"
        ARRENDATARIO = "arrendatario", "Arrendatario"

    tipo_entidad = models.CharField(max_length=20, choices=TipoEntidad.choices)
    entidad_id = models.PositiveBigIntegerField(
        help_text="PK del Propietario o Arrendatario según tipo_entidad",
    )
    nombre_o_razon_social = models.CharField(max_length=255)
    rfc = models.CharField("RFC", max_length=13)
    regimen_fiscal = models.CharField(max_length=100)
    uso_cfdi = models.CharField("Uso CFDI", max_length=10)
    codigo_postal = models.CharField(max_length=5)
    correo_facturacion = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "datos_fiscales"
        verbose_name = "Datos fiscales"
        verbose_name_plural = "Datos fiscales"
        indexes = [
            models.Index(fields=["tipo_entidad", "entidad_id"]),
        ]

    def __str__(self):
        return f"{self.rfc} — {self.nombre_o_razon_social}"
