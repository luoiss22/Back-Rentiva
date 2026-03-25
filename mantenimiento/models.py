from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg


class Especialista(models.Model):
    """Profesional de mantenimiento (marketplace)."""

    nombre = models.CharField(max_length=200)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    ciudad = models.CharField(max_length=120, blank=True)
    estado_geografico = models.CharField(max_length=120, blank=True)
    calificacion = models.DecimalField(
        max_digits=3, decimal_places=2, default=0,
    )
    anios_experiencia = models.PositiveSmallIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "especialistas"
        ordering = ["-calificacion"]
        verbose_name = "Especialista"
        verbose_name_plural = "Especialistas"

    def __str__(self):
        return f"{self.nombre} — {self.especialidad}"

    def recalcular_calificacion(self):
        """Recalcula el promedio de reseñas y guarda el campo calificacion."""
        promedio = self.resenas.aggregate(avg=Avg("calificacion"))["avg"]
        self.calificacion = round(promedio, 2) if promedio is not None else 0
        self.save(update_fields=["calificacion"])



class ReporteMantenimiento(models.Model):
    """Reporte de mantenimiento solicitado por el propietario."""

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_PROCESO = "en_proceso", "En proceso"
        RESUELTO = "resuelto", "Resuelto"
        CANCELADO = "cancelado", "Cancelado"

    propiedad = models.ForeignKey(
        "propiedades.Propiedad",
        on_delete=models.CASCADE,
        related_name="reportes",
    )
    especialista = models.ForeignKey(
        Especialista,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes",
    )
    propietario = models.ForeignKey(
        "autenticacion.Propietario",
        on_delete=models.CASCADE,
        related_name="reportes_mantenimiento",
    )
    descripcion = models.TextField()
    tipo_especialista = models.CharField(max_length=100, blank=True)
    prioridad = models.CharField(
        max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA,
    )
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.ABIERTO,
    )
    costo_estimado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    costo_final = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reportes_mantenimiento"
        ordering = ["-created_at"]
        verbose_name = "Reporte de mantenimiento"
        verbose_name_plural = "Reportes de mantenimiento"

    def __str__(self):
        return f"Reporte #{self.pk} — {self.propiedad} ({self.estado})"


class ResenaEspecialista(models.Model):
    """Reseña de un propietario hacia un especialista."""

    especialista = models.ForeignKey(
        Especialista,
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    propietario = models.ForeignKey(
        "autenticacion.Propietario",
        on_delete=models.CASCADE,
        related_name="resenas_escritas",
    )
    reporte = models.ForeignKey(
        ReporteMantenimiento,
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    calificacion = models.PositiveSmallIntegerField(
        help_text="Calificación de 1 a 5",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resenas_especialistas"
        ordering = ["-created_at"]
        verbose_name = "Reseña de especialista"
        verbose_name_plural = "Reseñas de especialistas"
        unique_together = ("propietario", "reporte")

    def __str__(self):
        return f"★{self.calificacion} — {self.especialista}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.especialista.recalcular_calificacion()

    def delete(self, *args, **kwargs):
        especialista = self.especialista
        super().delete(*args, **kwargs)
        especialista.recalcular_calificacion()
