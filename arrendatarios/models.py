from django.db import models


class Arrendatario(models.Model):
    """Inquilino / arrendatario de una propiedad."""

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    nombre = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    folio_ine = models.CharField(max_length=20, blank=True)
    mascotas = models.BooleanField(default=False)
    hijos = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "arrendatarios"
        ordering = ["apellidos", "nombre"]
        verbose_name = "Arrendatario"
        verbose_name_plural = "Arrendatarios"

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
